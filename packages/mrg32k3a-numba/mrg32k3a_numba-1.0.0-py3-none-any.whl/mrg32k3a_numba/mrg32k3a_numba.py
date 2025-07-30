#!/usr/bin/env python
"""
This module provides a Numba-accelerated implementation of the MRG32k3a random
number generator.

The MRG32k3a generator is a combined multiple recursive generator with a long
period, good statistical properties, and support for streams and substreams.
This implementation, `MRG32k3a_numba`, is designed for high-performance
simulations in Python, leveraging Numba's just-in-time (JIT) compilation for
C-like speed.

Key Features:
- **High Performance:** Core generator logic and statistical distributions are
  accelerated using Numba.
- **Stream/Substream/Subsubstream Support:** Allows for the creation of
  independent random number sequences, crucial for parallel and distributed
- **Reproducibility:** Guarantees that the same seed and stream indices will
  always produce the same sequence of random numbers.
- **Variety of Distributions:** Includes methods for generating random variates
  from uniform, normal, exponential, log-normal, triangular, gamma, beta,
  and other common statistical distributions.

The implementation uses matrix-based state advancement ("jumping") to efficiently
navigate between streams. The jump sizes are:
- Subsubstream: 2^47 steps
- Substream: 2^94 steps
- Stream: 2^141 steps
"""
from __future__ import annotations

import math

import numpy as np
from numba import njit, types
from numba.experimental import jitclass

# =============================================================================
# Constants and Base Matrices for MRG32k3a
# These constants define the recurrence relations for the two components of
# the combined MRG.
# =============================================================================

# Moduli for the two MRG components
mrgm1 = np.int64(4294967087)  # m1 = 2^32 - 209
mrgm2 = np.int64(4294944443)  # m2 = 2^32 - 22853

# Coefficients for the first MRG component's recurrence relation:
# X_n = (a12 * X_{n-2} - a13n * X_{n-3}) mod m1
mrga12 = np.int64(1403580)
mrga13n = np.int64(810728)  # Note: This is the negative of the original a13

# Coefficients for the second MRG component's recurrence relation:
# Y_n = (a21 * Y_{n-1} - a23n * Y_{n-3}) mod m2
mrga21 = np.int64(527612)
mrga23n = np.int64(1370589)  # Note: This is the negative of the original a23

# State transition matrices derived from the recurrence relations.
# These matrices are used to advance the generator's state.
A1p0 = np.array([[0, 1, 0], [0, 0, 1], [-mrga13n, mrga12, 0]], dtype=np.int64)
A2p0 = np.array([[0, 1, 0], [0, 0, 1], [-mrga23n, 0, mrga21]], dtype=np.int64)


# =============================================================================
# Numba-JITted Helper Functions for Modular Arithmetic
# These functions are optimized for performance with Numba's JIT compiler.
# =============================================================================

@njit(cache=True, inline='always')
def mult_mod_careful(a: np.int64, b: np.int64, m: np.int64) -> np.int64:
    """Computes (a * b) % m, preventing overflow for large 64-bit integers.

    Standard multiplication of two 64-bit integers can exceed the maximum
    value for np.int64, leading to incorrect results. This function uses
    double-precision floating-point numbers for the intermediate product
    to maintain precision and correctly compute the modulus.

    Args:
        a (np.int64): The first integer.
        b (np.int64): The second integer.
        m (np.int64): The modulus.

    Returns:
        np.int64: The result of (a * b) % m.
    """
    # Ensure operands are in the range [0, m-1]
    a = a % m
    b = b % m
    if a < 0:
        a += m
    if b < 0:
        b += m

    # Use float64 for the intermediate product to avoid overflow
    result = np.float64(a) * np.float64(b)

    # Calculate the remainder
    q = np.int64(result / np.float64(m))
    r = np.int64(a) * np.int64(b) - q * m

    # Ensure the remainder is positive
    while r < 0:
        r += m
    while r >= m:
        r -= m

    return r


@njit(cache=True)
def mat33_mat33_mult_mod(A: np.ndarray, B: np.ndarray, m: np.int64) -> np.ndarray:
    """Computes the product of two 3x3 matrices with modular arithmetic.

    Args:
        A (np.ndarray): The first 3x3 matrix (dtype=np.int64).
        B (np.ndarray): The second 3x3 matrix (dtype=np.int64).
        m (np.int64): The modulus.

    Returns:
        np.ndarray: The resulting 3x3 matrix (A @ B) % m.
    """
    C = np.zeros((3, 3), dtype=np.int64)
    for i in range(3):
        for j in range(3):
            sum_val = np.int64(0)
            for k in range(3):
                prod = mult_mod_careful(A[i, k], B[k, j], m)
                sum_val = (sum_val + prod) % m
                if sum_val < 0:
                    sum_val += m
            C[i, j] = sum_val
    return C


@njit(cache=True)
def mat33_mat31_mult_mod(A: np.ndarray, v: np.ndarray, m: np.int64) -> np.ndarray:
    """Computes the product of a 3x3 matrix and a 3x1 vector with modular arithmetic.

    Args:
        A (np.ndarray): The 3x3 matrix (dtype=np.int64).
        v (np.ndarray): The 3x1 vector (dtype=np.int64).
        m (np.int64): The modulus.

    Returns:
        np.ndarray: The resulting 3x1 vector (A @ v) % m.
    """
    res = np.zeros(3, dtype=np.int64)
    for i in range(3):
        sum_val = np.int64(0)
        for j in range(3):
            prod = mult_mod_careful(A[i, j], v[j], m)
            sum_val = (sum_val + prod) % m
            if sum_val < 0:
                sum_val += m
        res[i] = sum_val
    return res


@njit(cache=True)
def mat33_power_mod(A: np.ndarray, n: int, m: np.int64) -> np.ndarray:
    """Computes A^n mod m for a 3x3 matrix using binary exponentiation (exponentiation by squaring).

    Args:
        A (np.ndarray): The 3x3 matrix (base).
        n (int): The exponent.
        m (np.int64): The modulus.

    Returns:
        np.ndarray: The resulting 3x3 matrix (A^n % m).
    """
    B = np.eye(3, dtype=np.int64)
    A_work = A.copy()

    while n > 0:
        if n % 2 == 1:
            B = mat33_mat33_mult_mod(A_work, B, m)
        A_work = mat33_mat33_mult_mod(A_work, A_work, m)
        n = n // 2

    return B


@njit(cache=True)
def mat33_power_of_2_mod(A: np.ndarray, k: int, m: np.int64) -> np.ndarray:
    """Computes A^(2^k) mod m for a 3x3 matrix using repeated squaring.

    This is more efficient than `mat33_power_mod` when the exponent is a power of 2.

    Args:
        A (np.ndarray): The 3x3 matrix (base).
        k (int): The power of 2 in the exponent.
        m (np.int64): The modulus.

    Returns:
        np.ndarray: The resulting 3x3 matrix (A^(2^k) % m).
    """
    res = A.copy()
    for _ in range(k):
        res = mat33_mat33_mult_mod(res, res, m)
    return res


# =============================================================================
# Pre-computed Global Jump Matrices
# These matrices are computed once when the module is loaded. They represent
# jumps of 2^47, 2^94, and 2^141 steps, corresponding to advancing to the next
# subsubstream, substream, and stream, respectively.
# =============================================================================
@njit(cache=True)
def get_jump_matrices():
    """Computes and returns the jump-ahead matrices used for streams.

    Returns:
        tuple[np.ndarray, ...]: A tuple containing the pre-computed jump
        matrices (A1p47, A2p47, A1p94, A2p94, A1p141, A2p141).
    """
    A1p0_local = np.array([[0, 1, 0], [0, 0, 1], [-810728, 1403580, 0]], dtype=np.int64)
    A2p0_local = np.array([[0, 1, 0], [0, 0, 1], [-1370589, 0, 527612]], dtype=np.int64)

    # Jump matrix for one subsubstream (2^47 steps)
    A1p47 = mat33_power_of_2_mod(A1p0_local, 47, mrgm1)
    A2p47 = mat33_power_of_2_mod(A2p0_local, 47, mrgm2)
    # Jump matrix for one substream (2^94 steps)
    A1p94 = mat33_power_of_2_mod(A1p0_local, 94, mrgm1)
    A2p94 = mat33_power_of_2_mod(A2p0_local, 94, mrgm2)
    # Jump matrix for one stream (2^141 steps)
    A1p141 = mat33_power_of_2_mod(A1p0_local, 141, mrgm1)
    A2p141 = mat33_power_of_2_mod(A2p0_local, 141, mrgm2)

    return A1p47, A2p47, A1p94, A2p94, A1p141, A2p141


# Unpack the pre-computed matrices into global, Numba-accessible variables.
A1p47_g, A2p47_g, A1p94_g, A2p94_g, A1p141_g, A2p141_g = get_jump_matrices()

# =============================================================================
# Core RNG and Distribution Functions
# =============================================================================

# Pre-calculated inverse for normalization to a U(0,1) variate.
MRG_M1_PLUS_1_INV = 1.0 / (mrgm1 + 1)


@njit(cache=True, inline='always')
def mrg32k3a_generator(state: tuple[int, int, int, int, int, int]) -> tuple[tuple, float]:
    """Generates one random number using the MRG32k3a algorithm.

    Args:
        state (tuple): A tuple of 6 integers representing the current state
                       (s10, s11, s12, s20, s21, s22).

    Returns:
        tuple[tuple, float]: A tuple containing the new state and the
                             generated uniform random number in (0, 1).
    """
    s10, s11, s12, s20, s21, s22 = state

    # First MRG component
    p1 = (mrga12 * s11 - mrga13n * s10) % mrgm1
    if p1 < 0:
        p1 += mrgm1

    # Second MRG component
    p2 = (mrga21 * s22 - mrga23n * s20) % mrgm2
    if p2 < 0:
        p2 += mrgm2

    # New state for the next iteration
    new_state = (s11, s12, p1, s21, s22, p2)

    # Combine the two components
    z = (p1 - p2) % mrgm1
    if z < 0:
        z += mrgm1

    # Convert to a uniform random variate in (0, 1)
    if z > 0:
        u = z * MRG_M1_PLUS_1_INV
    else:
        # Handle the case z=0 to maintain the (0, 1) interval
        u = mrgm1 * MRG_M1_PLUS_1_INV

    return new_state, u


# Constants for the Beasley-Springer-Moro (BSM) algorithm, which approximates
# the inverse of the standard normal cumulative distribution function (CDF).
bsma = np.array([2.50662823884, -18.61500062529, 41.39119773534, -25.44106049637], dtype=np.float64)
bsmb = np.array([-8.47351093090, 23.08336743743, -21.06224101826, 3.13082909833], dtype=np.float64)
bsmc = np.array([0.3374754822726147, 0.9761690190917186, 0.1607979714918209, 0.0276438810333863,
                 0.0038405729373609, 0.0003951896511919, 0.0000321767881768, 0.0000002888167364,
                 0.0000003960315187], dtype=np.float64)


@njit(cache=True)
def bsm(u: float) -> float:
    """Approximates the inverse standard normal CDF using the Beasley-Springer-Moro algorithm.

    Args:
        u (float): A uniform random number in (0, 1).

    Returns:
        float: A standard normal random variate.
    """
    y = u - 0.5
    if abs(y) < 0.42:
        # Use a rational approximation for the central region of the distribution
        r = y * y
        z = y * (((bsma[3] * r + bsma[2]) * r + bsma[1]) * r + bsma[0]) / (
                (((bsmb[3] * r + bsmb[2]) * r + bsmb[1]) * r + bsmb[0]) * r + 1.0)
    else:
        # Use a log-based approximation for the tails
        r = u
        if y > 0:
            r = 1.0 - u
        s = math.log(-math.log(r))
        t = bsmc[0]
        for i in range(1, 9):
            t += bsmc[i] * (s ** i)
        if y < 0:
            z = -t
        else:
            z = t
    return z


@njit(cache=True)
def _gamma_helper(alpha, random_func, normal_func):
    """
    Numba-jitted helper for generating gamma variates.
    Uses Marsaglia and Tsang's method for alpha >= 1.
    """
    if alpha < 1.0:
        # Boost alpha for the main algorithm, then scale the result down.
        # This uses the property that if X ~ Gamma(a+1, 1), then X*U^(1/a) ~ Gamma(a, 1)
        g = _gamma_helper(alpha + 1.0, random_func, normal_func)
        return g * (random_func() ** (1.0 / alpha))
    else:
        # Marsaglia and Tsang's method for alpha >= 1
        d = alpha - 1.0 / 3.0
        c = 1.0 / math.sqrt(9.0 * d)
        while True:
            x = normal_func(0.0, 1.0)
            v = 1.0 + c * x
            if v <= 0:
                continue
            v = v * v * v
            u = random_func()
            x_squared = x * x
            if u < 1.0 - 0.0331 * x_squared * x_squared:
                return d * v
            if math.log(u) < 0.5 * x_squared + d * (1.0 - v + math.log(v)):
                return d * v


# =============================================================================
# JIT Class for the MRG32k3a Generator
# This class encapsulates the state and methods of the RNG.
# =============================================================================

# This 'spec' defines the data types for the class attributes. It is required
# by numba.jitclass for AOT (Ahead-Of-Time) compilation, enabling significant
# performance gains.
spec = [
    ('_current_state', types.UniTuple(types.int64, 6)),
    ('ref_seed', types.UniTuple(types.int64, 6)),
    ('s_ss_sss_index', types.int64[:]),
    ('stream_start', types.UniTuple(types.int64, 6)),
    ('substream_start', types.UniTuple(types.int64, 6)),
    ('subsubstream_start', types.UniTuple(types.int64, 6)),
]


@jitclass(spec)
class MRG32k3a_numba:
    """A Numba-accelerated MRG32k3a random number generator with stream support.

    This class provides a fast, full-featured random number generator suitable
    for parallel simulations. It uses a default seed and allows navigation
    through a structured sequence of random numbers via streams, substreams,
    and subsubstreams.

    Attributes:
        _current_state (tuple): The internal 6-integer state of the generator.
        ref_seed (tuple): The base seed from which all streams are derived.
        s_ss_sss_index (np.ndarray): A 3-element array holding the current
                                    [stream, substream, subsubstream] indices.
        stream_start (tuple): The state at the beginning of the current stream.
        substream_start (tuple): The state at the beginning of the current substream.
        subsubstream_start (tuple): The state at the beginning of the current subsubstream.
    """

    def __init__(self, s_ss_sss_index: np.ndarray):
        """Initializes the MRG32k3a generator for a specific stream.

        Args:
            s_ss_sss_index (np.ndarray): A 1D numpy array of 3 integers
                representing the initial (stream, substream, subsubstream)
                indices. Example: np.array([0, 0, 0], dtype=np.int64)
        """
        # The reference seed is fixed to ensure reproducibility across different
        # runs and platforms. All streams are offsets from this single seed.
        self.ref_seed = (np.int64(12345), np.int64(12345), np.int64(12345),
                         np.int64(12345), np.int64(12345), np.int64(12345))

        # Initialize tracking variables
        self.s_ss_sss_index = s_ss_sss_index.copy()
        self.stream_start = self.ref_seed
        self.substream_start = self.ref_seed
        self.subsubstream_start = self.ref_seed
        self._current_state = self.ref_seed

        # Jump to the specified starting point in the sequence
        self.start_fixed_s_ss_sss(s_ss_sss_index)

    def seed(self, new_state: tuple[int, int, int, int, int, int]):
        """Sets the internal state of the generator directly.

        Note:
            This is a low-level function. For most use cases, it is recommended
            to use the stream management methods (`advance_stream`, `reset_stream`, etc.)
            to ensure non-overlapping sequences.

        Args:
            new_state (tuple): A 6-integer tuple for the new state.
        """
        self._current_state = new_state

    def random(self) -> float:
        """Returns the next random floating point number in the range (0.0, 1.0)."""
        new_state, u = mrg32k3a_generator(self._current_state)
        self._current_state = new_state
        return u

    def normalvariate(self, mu: float, sigma: float) -> float:
        """Returns a normal random variate.

        Args:
            mu (float): The mean of the normal distribution.
            sigma (float): The standard deviation of the normal distribution.

        Returns:
            float: A random number from the N(mu, sigma) distribution.
        """
        # Note: When calling from a Numba-jitted function, all arguments must be
        # provided positionally (e.g., rng.normalvariate(0.0, 1.0)).
        u = self.random()
        z = bsm(u)
        return mu + sigma * z

    def expovariate(self, lmbda: float) -> float:
        """Returns an exponentially distributed random number.

        Args:
            lmbda (float): The rate parameter (1/mean). Must be non-zero.

        Returns:
            float: A random number from the exponential distribution.
        """
        u = self.random()
        # Use inverse transform sampling: -ln(1-U)/lambda
        return -math.log(1.0 - u) / lmbda

    def uniform(self, a: float, b: float) -> float:
        """Returns a random floating point number N such that a <= N < b.

        Args:
            a (float): The lower bound of the range.
            b (float): The upper bound of the range.

        Returns:
            float: A random number from the U[a, b) distribution.
        """
        u = self.random()
        return a + (b - a) * u

    def gauss(self, mu: float, sigma: float) -> float:
        """Alias for normalvariate."""
        return self.normalvariate(mu, sigma)

    def lognormalvariate(self, mu: float, sigma: float) -> float:
        """Returns a log-normally distributed random number.

        The logarithm of this variate will be normally distributed with mean `mu`
        and standard deviation `sigma`.

        Args:
            mu (float): The mean of the underlying normal distribution.
            sigma (float): The standard deviation of the underlying normal distribution.

        Returns:
            float: A random number from the log-normal distribution.
        """
        return math.exp(self.normalvariate(mu, sigma))

    def triangular(self, low: float, high: float, mode: float) -> float:
        """Returns a random number from a triangular distribution.

        Args:
            low (float): The lower bound of the distribution.
            high (float): The upper bound of the distribution.
            mode (float): The peak (most common value) of the distribution.

        Returns:
            float: A random number from the triangular distribution.
        """
        # Note: When calling from a Numba-jitted function, all arguments must
        # be provided positionally.
        u = self.random()
        c = (mode - low) / (high - low)
        if u < c:
            return low + math.sqrt(u * (high - low) * (mode - low))
        else:
            return high - math.sqrt((1.0 - u) * (high - low) * (high - mode))

    def gammavariate(self, alpha: float, beta: float) -> float:
        """Returns a gamma-distributed random number.

        Args:
            alpha (float): The shape parameter (k). Must be > 0.
            beta (float): The scale parameter (theta). Must be > 0.

        Returns:
            float: A random number from the gamma distribution.
        """
        if alpha <= 0.0 or beta <= 0.0:
            # Raising exceptions from jitclass is complex, return NaN instead.
            return np.nan
        # Generate a Gamma(alpha, 1) and then scale by beta
        return _gamma_helper(alpha, self.random, self.normalvariate) * beta

    def betavariate(self, alpha: float, beta: float) -> float:
        """Returns a beta-distributed random number.

        Args:
            alpha (float): The first shape parameter. Must be > 0.
            beta (float): The second shape parameter. Must be > 0.

        Returns:
            float: A random number from the beta distribution.
        """
        if alpha <= 0.0 or beta <= 0.0:
            return np.nan
        # Use the property that if Y1 ~ Gamma(a,1) and Y2 ~ Gamma(b,1),
        # then Y1 / (Y1+Y2) ~ Beta(a,b).
        y1 = self.gammavariate(alpha, 1.0)
        y2 = self.gammavariate(beta, 1.0)
        return y1 / (y1 + y2)

    def weibullvariate(self, alpha: float, beta: float) -> float:
        """Returns a Weibull-distributed random number.

        Args:
            alpha (float): The scale parameter (lambda).
            beta (float): The shape parameter (k).

        Returns:
            float: A random number from the Weibull distribution.
        """
        u = self.random()
        return alpha * ((-math.log(1.0 - u)) ** (1.0 / beta))

    def paretovariate(self, alpha: float) -> float:
        """Returns a Pareto-distributed random number.

        Args:
            alpha (float): The shape parameter.

        Returns:
            float: A random number from the Pareto Type I distribution.
        """
        u = self.random()
        return (1.0 - u) ** (-1.0 / alpha)

    def poissonvariate(self, lmbda: float) -> int:
        """Returns a Poisson-distributed random number.

        Args:
            lmbda (float): The expected value (lambda) of the distribution.

        Returns:
            int: A random integer from the Poisson distribution.
        """
        if lmbda < 35.0:
            # Knuth's algorithm for small lambda
            p = self.random()
            threshold = math.exp(-lmbda)
            n = 0
            while p >= threshold:
                u = self.random()
                p = p * u
                n = n + 1
            return n
        else:
            # Normal approximation for large lambda
            z = self.normalvariate(0.0, 1.0)
            n = max(int(lmbda + math.sqrt(lmbda) * z + 0.5), 0)
            return n

    def gumbelvariate(self, mu: float, beta: float) -> float:
        """Returns a Gumbel-distributed random number.

        Args:
            mu (float): The location of the mode.
            beta (float): The scale parameter (> 0).

        Returns:
            float: A random number from the Gumbel distribution.
        """
        u = self.random()
        return mu - beta * math.log(-math.log(u))

    def binomialvariate(self, n: int, p: float) -> int:
        """Returns a binomial-distributed random number.

        This implementation simulates n Bernoulli trials.

        Args:
            n (int): The number of trials (> 0).
            p (float): The success probability for each trial (0 <= p <= 1).

        Returns:
            int: The number of successes.
        """
        successes = 0
        for _ in range(n):
            if self.random() < p:
                successes += 1
        return successes

    def mvnormalvariate(self, mean_vec: np.ndarray, cov: np.ndarray) -> np.ndarray:
        """Generate a normal random vector.

        Args:
            mean_vec (np.ndarray): 1D array for the mean vector.
            cov (np.ndarray): 2D array for the covariance matrix.

        Returns:
            np.ndarray: A multivariate normal random vector.
        """
        n_cols = len(cov)
        chol = np.linalg.cholesky(cov)

        observations = np.empty(n_cols, dtype=np.float64)
        for i in range(n_cols):
            observations[i] = self.normalvariate(0.0, 1.0)

        return chol @ observations + mean_vec

    def continuous_random_vector_from_simplex(self, n_elements: int, summation: float, exact_sum: bool) -> np.ndarray:
        """Generates a random vector of non-negative reals that sum to a value.

        Args:
            n_elements (int): Number of elements in the vector.
            summation (float): The target sum.
            exact_sum (bool): If True, sum is exactly `summation`.
                              If False, sum is <= `summation`.
        Returns:
            np.ndarray: A vector of non-negative real numbers.
        """
        if exact_sum:
            exp_rvs = np.empty(n_elements, dtype=np.float64)
            for i in range(n_elements):
                exp_rvs[i] = self.expovariate(1.0)

            exp_sum = np.sum(exp_rvs)
            return (summation * exp_rvs) / exp_sum
        else:
            unif_rvs = np.empty(n_elements, dtype=np.float64)
            for i in range(n_elements):
                unif_rvs[i] = self.random()

            unif_rvs.sort()

            x = np.empty(n_elements + 2, dtype=np.float64)
            x[0] = 0.0
            x[1:-1] = unif_rvs
            x[-1] = 1.0

            diffs = np.diff(x)

            # vertices = np.vstack((np.zeros(n_elements), np.eye(n_elements)))
            vertices = np.vstack((np.zeros((1, n_elements), dtype=np.float64), np.eye(n_elements)))

            vec = summation * np.sum(vertices * diffs.reshape(-1, 1), axis=0)
            return vec

    def start_fixed_s_ss_sss(self, s_ss_sss_triplet: np.ndarray):
        """Jumps the generator state to the beginning of a specified stream triplet.

        This method sequentially applies matrix powers to the reference seed to
        calculate the start state of the target (stream, substream, subsubstream)
        without generating intermediate random numbers.

        Args:
            s_ss_sss_triplet (np.ndarray): A 3-element array specifying the
                target [stream, substream, subsubstream] indices.
        """
        # Start with the global reference seed
        st1 = np.array([self.ref_seed[0], self.ref_seed[1], self.ref_seed[2]], dtype=np.int64)
        st2 = np.array([self.ref_seed[3], self.ref_seed[4], self.ref_seed[5]], dtype=np.int64)

        # 1. Advance to the start of the target stream
        if s_ss_sss_triplet[0] > 0:
            power_mod_1 = mat33_power_mod(A1p141_g, s_ss_sss_triplet[0], mrgm1)
            power_mod_2 = mat33_power_mod(A2p141_g, s_ss_sss_triplet[0], mrgm2)
            st1 = mat33_mat31_mult_mod(power_mod_1, st1, mrgm1)
            st2 = mat33_mat31_mult_mod(power_mod_2, st2, mrgm2)
        self.stream_start = (st1[0], st1[1], st1[2], st2[0], st2[1], st2[2])

        # 2. From stream start, advance to the start of the target substream
        if s_ss_sss_triplet[1] > 0:
            power_mod_1 = mat33_power_mod(A1p94_g, s_ss_sss_triplet[1], mrgm1)
            power_mod_2 = mat33_power_mod(A2p94_g, s_ss_sss_triplet[1], mrgm2)
            st1 = mat33_mat31_mult_mod(power_mod_1, st1, mrgm1)
            st2 = mat33_mat31_mult_mod(power_mod_2, st2, mrgm2)
        self.substream_start = (st1[0], st1[1], st1[2], st2[0], st2[1], st2[2])

        # 3. From substream start, advance to the start of the target subsubstream
        if s_ss_sss_triplet[2] > 0:
            power_mod_1 = mat33_power_mod(A1p47_g, s_ss_sss_triplet[2], mrgm1)
            power_mod_2 = mat33_power_mod(A2p47_g, s_ss_sss_triplet[2], mrgm2)
            st1 = mat33_mat31_mult_mod(power_mod_1, st1, mrgm1)
            st2 = mat33_mat31_mult_mod(power_mod_2, st2, mrgm2)
        self.subsubstream_start = (st1[0], st1[1], st1[2], st2[0], st2[1], st2[2])

        # Set the current state and update indices
        self.seed(self.subsubstream_start)
        self.s_ss_sss_index[0] = s_ss_sss_triplet[0]
        self.s_ss_sss_index[1] = s_ss_sss_triplet[1]
        self.s_ss_sss_index[2] = s_ss_sss_triplet[2]

    def advance_stream(self):
        """Advances the generator to the start of the next stream.

        This jumps the state forward by 2^141 steps.
        """
        st1 = np.array([self.stream_start[0], self.stream_start[1], self.stream_start[2]], dtype=np.int64)
        st2 = np.array([self.stream_start[3], self.stream_start[4], self.stream_start[5]], dtype=np.int64)

        nst1 = mat33_mat31_mult_mod(A1p141_g, st1, mrgm1)
        nst2 = mat33_mat31_mult_mod(A2p141_g, st2, mrgm2)
        nstate = (nst1[0], nst1[1], nst1[2], nst2[0], nst2[1], nst2[2])

        # Update all state trackers to the new stream's start
        self.seed(nstate)
        self.stream_start = nstate
        self.substream_start = nstate
        self.subsubstream_start = nstate

        # Update indices
        self.s_ss_sss_index[0] += 1
        self.s_ss_sss_index[1] = 0
        self.s_ss_sss_index[2] = 0

    def advance_substream(self):
        """Advances the generator to the start of the next substream.

        This jumps the state forward by 2^94 steps from the start of the
        current substream.
        """
        st1 = np.array([self.substream_start[0], self.substream_start[1], self.substream_start[2]], dtype=np.int64)
        st2 = np.array([self.substream_start[3], self.substream_start[4], self.substream_start[5]], dtype=np.int64)

        nst1 = mat33_mat31_mult_mod(A1p94_g, st1, mrgm1)
        nst2 = mat33_mat31_mult_mod(A2p94_g, st2, mrgm2)
        nstate = (nst1[0], nst1[1], nst1[2], nst2[0], nst2[1], nst2[2])

        # Update state trackers
        self.seed(nstate)
        self.substream_start = nstate
        self.subsubstream_start = nstate

        # Update indices
        self.s_ss_sss_index[1] += 1
        self.s_ss_sss_index[2] = 0

    def advance_subsubstream(self):
        """Advances the generator to the start of the next subsubstream.

        This jumps the state forward by 2^47 steps from the start of the
        current subsubstream.
        """
        st1 = np.array([self.subsubstream_start[0], self.subsubstream_start[1], self.subsubstream_start[2]],
                       dtype=np.int64)
        st2 = np.array([self.subsubstream_start[3], self.subsubstream_start[4], self.subsubstream_start[5]],
                       dtype=np.int64)

        nst1 = mat33_mat31_mult_mod(A1p47_g, st1, mrgm1)
        nst2 = mat33_mat31_mult_mod(A2p47_g, st2, mrgm2)
        nstate = (nst1[0], nst1[1], nst1[2], nst2[0], nst2[1], nst2[2])

        # Update state trackers
        self.seed(nstate)
        self.subsubstream_start = nstate

        # Update index
        self.s_ss_sss_index[2] += 1

    def reset_stream(self):
        """Resets the generator to the start of the current stream."""
        nstate = self.stream_start
        self.seed(nstate)
        self.substream_start = nstate
        self.subsubstream_start = nstate
        self.s_ss_sss_index[1] = 0
        self.s_ss_sss_index[2] = 0

    def reset_substream(self):
        """Resets the generator to the start of the current substream."""
        nstate = self.substream_start
        self.seed(nstate)
        self.subsubstream_start = nstate
        self.s_ss_sss_index[2] = 0

    def reset_subsubstream(self):
        """Resets the generator to the start of the current subsubstream."""
        nstate = self.subsubstream_start
        self.seed(nstate)

    def get_current_state(self) -> tuple[int, int, int, int, int, int]:
        """Returns the current internal state of the generator.

        Returns:
            tuple: A 6-integer tuple representing the current state.
        """
        return self._current_state