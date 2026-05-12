"""Bayesian prior distributions for latent beneficial-ownership shares.

Implements Beta and truncated-Normal priors. NumPyro distributions are used
when numpyro is available; a pure-numpy fallback is provided for environments
where numpyro/JAX are not installed.
"""

from __future__ import annotations

from typing import Any


class BetaPrior:
    """Beta prior distribution on latent ownership shares in [0, 1].

    Args:
        alpha: First concentration parameter. alpha=1 with beta=1 gives Uniform.
        beta: Second concentration parameter.

    Examples:
        >>> p = BetaPrior(alpha=2.0, beta=5.0)
        >>> p.alpha
        2.0
        >>> p.log_prob(0.3) < 0
        True
    """

    def __init__(self, alpha: float = 2.0, beta: float = 5.0) -> None:
        if alpha <= 0 or beta <= 0:
            raise ValueError(f"alpha and beta must be positive, got {alpha}, {beta}")
        self.alpha = alpha
        self.beta = beta

    def log_prob(self, x: Any) -> Any:
        """Compute log probability density.

        Args:
            x: Value in (0, 1).

        Returns:
            Log probability density (scalar or array).

        Examples:
            >>> p = BetaPrior(1.0, 1.0)
            >>> abs(p.log_prob(0.5)) < 1e-10
            True
        """
        try:
            import jax.numpy as jnp
            import numpyro.distributions as dist

            d = dist.Beta(self.alpha, self.beta)
            return d.log_prob(jnp.asarray(x))
        except ImportError:
            import math

            import numpy as np

            x_arr = np.asarray(x, dtype=np.float64)
            log_b = (
                math.lgamma(self.alpha)
                + math.lgamma(self.beta)
                - math.lgamma(self.alpha + self.beta)
            )
            return (self.alpha - 1) * np.log(x_arr) + (self.beta - 1) * np.log(1 - x_arr) - log_b

    def sample(self, n: int, seed: int = 0) -> Any:
        """Draw n samples from the prior.

        Args:
            n: Number of samples.
            seed: Random seed.

        Returns:
            Array of shape (n,) with values in (0, 1).

        Examples:
            >>> p = BetaPrior(2.0, 5.0)
            >>> s = p.sample(10, seed=42)
            >>> len(s) == 10
            True
        """
        try:
            import jax
            import numpyro.distributions as dist

            key = jax.random.PRNGKey(seed)
            d = dist.Beta(self.alpha, self.beta)
            return d.sample(key, (n,))
        except ImportError:
            import numpy as np

            rng = np.random.default_rng(seed)
            return rng.beta(self.alpha, self.beta, size=n)


class TruncatedNormalPrior:
    """Truncated-Normal prior on latent ownership shares, truncated to [0, 1].

    Args:
        loc: Mean of the underlying Normal distribution.
        scale: Standard deviation of the underlying Normal distribution.

    Examples:
        >>> p = TruncatedNormalPrior(loc=0.5, scale=0.2)
        >>> p.loc
        0.5
    """

    def __init__(self, loc: float = 0.5, scale: float = 0.2) -> None:
        if scale <= 0:
            raise ValueError(f"scale must be positive, got {scale}")
        self.loc = loc
        self.scale = scale

    def log_prob(self, x: Any) -> Any:
        """Compute log probability density (unnormalised within [0, 1]).

        Args:
            x: Value in [0, 1].

        Returns:
            Log probability density.

        Examples:
            >>> p = TruncatedNormalPrior(0.5, 0.2)
            >>> isinstance(float(p.log_prob(0.5)), float)
            True
        """
        try:
            import jax.numpy as jnp
            import numpyro.distributions as dist

            d = dist.TruncatedNormal(loc=self.loc, scale=self.scale, low=0.0, high=1.0)
            return d.log_prob(jnp.asarray(x))
        except ImportError:
            import numpy as np

            x_arr = np.asarray(x, dtype=np.float64)
            z = (x_arr - self.loc) / self.scale
            return -0.5 * z**2 - np.log(self.scale) - 0.5 * np.log(2 * np.pi)

    def sample(self, n: int, seed: int = 0) -> Any:
        """Draw n samples truncated to [0, 1].

        Args:
            n: Number of samples.
            seed: Random seed.

        Returns:
            Array of shape (n,) with values in [0, 1].

        Examples:
            >>> p = TruncatedNormalPrior(0.5, 0.2)
            >>> s = p.sample(10, seed=42)
            >>> len(s) == 10
            True
        """
        try:
            import jax
            import numpyro.distributions as dist

            key = jax.random.PRNGKey(seed)
            d = dist.TruncatedNormal(loc=self.loc, scale=self.scale, low=0.0, high=1.0)
            return d.sample(key, (n,))
        except ImportError:
            import numpy as np
            from scipy.stats import truncnorm

            a, b = (0.0 - self.loc) / self.scale, (1.0 - self.loc) / self.scale
            rng = np.random.default_rng(seed)
            return truncnorm.rvs(a, b, loc=self.loc, scale=self.scale, size=n, random_state=rng)
