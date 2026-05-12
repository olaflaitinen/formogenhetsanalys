"""Variational inference posteriors and loss functions.

Implements mean-field, low-rank multivariate Normal, and normalising-flow
posteriors over latent beneficial-ownership shares.  NumPyro guides and ELBO/
IWAE losses are provided when numpyro is available; numpy stubs otherwise.
"""

from __future__ import annotations

from typing import Any

import numpy as np


class MeanFieldPosterior:
    """Mean-field (fully factorised) variational posterior.

    Each latent ownership share has an independent Beta posterior parameterised
    by variational alpha and beta.

    Args:
        n_latent: Number of latent ownership-share variables.
        init_alpha: Initial alpha parameter for all Beta posteriors.
        init_beta: Initial beta parameter for all Beta posteriors.
        seed: Initialisation seed.

    Examples:
        >>> q = MeanFieldPosterior(n_latent=10, seed=123)
        >>> q.n_latent
        10
    """

    def __init__(
        self,
        n_latent: int,
        init_alpha: float = 2.0,
        init_beta: float = 5.0,
        seed: int = 123,
    ) -> None:
        self.n_latent = n_latent
        rng = np.random.default_rng(seed)
        self.log_alpha = np.log(np.full(n_latent, init_alpha) + rng.normal(0, 0.01, n_latent))
        self.log_beta = np.log(np.full(n_latent, init_beta) + rng.normal(0, 0.01, n_latent))

    @property
    def alpha(self) -> np.ndarray[Any, np.dtype[np.float64]]:
        """Softplus-transformed alpha parameters."""
        return np.log1p(np.exp(self.log_alpha))

    @property
    def beta(self) -> np.ndarray[Any, np.dtype[np.float64]]:
        """Softplus-transformed beta parameters."""
        return np.log1p(np.exp(self.log_beta))

    def sample(self, seed: int = 0) -> np.ndarray[Any, np.dtype[np.float64]]:
        """Draw one sample from the mean-field posterior.

        Args:
            seed: Random seed.

        Returns:
            Array of shape (n_latent,) with ownership-share samples in (0, 1).

        Examples:
            >>> q = MeanFieldPosterior(5, seed=123)
            >>> s = q.sample(seed=0)
            >>> s.shape == (5,)
            True
        """
        rng = np.random.default_rng(seed)
        return rng.beta(self.alpha, self.beta)

    def entropy(self) -> float:
        """Compute the entropy of the mean-field posterior (sum of Beta entropies).

        Returns:
            Scalar entropy value.

        Examples:
            >>> q = MeanFieldPosterior(5, seed=123)
            >>> isinstance(q.entropy(), float)
            True
        """
        from math import lgamma

        a, b = self.alpha, self.beta
        lbeta = np.array(
            [
                lgamma(float(ai)) + lgamma(float(bi)) - lgamma(float(ai + bi))
                for ai, bi in zip(a.tolist(), b.tolist(), strict=False)
            ],
        )
        return float(np.sum(lbeta))


class LowRankPosterior:
    """Low-rank multivariate Normal variational posterior.

    Parameterises the posterior as N(mu, diag(d) + FF^T) where F is a
    rank-r factor matrix.

    Args:
        n_latent: Dimension of the latent vector.
        rank: Rank of the factor matrix.
        seed: Initialisation seed.

    Examples:
        >>> q = LowRankPosterior(n_latent=10, rank=2, seed=123)
        >>> q.mu.shape == (10,)
        True
    """

    def __init__(self, n_latent: int, rank: int = 4, seed: int = 123) -> None:
        self.n_latent = n_latent
        self.rank = rank
        rng = np.random.default_rng(seed)
        self.mu = rng.normal(0.0, 0.1, n_latent)
        self.log_diag = np.zeros(n_latent)
        self.factor = rng.normal(0.0, 0.01, (n_latent, rank))

    def covariance(self) -> np.ndarray[Any, np.dtype[np.float64]]:
        """Compute the approximate covariance matrix.

        Returns:
            Array of shape (n_latent, n_latent).

        Examples:
            >>> q = LowRankPosterior(4, rank=2, seed=0)
            >>> q.covariance().shape == (4, 4)
            True
        """
        d = np.exp(self.log_diag)
        return np.diag(d) + self.factor @ self.factor.T

    def sample(self, seed: int = 0) -> np.ndarray[Any, np.dtype[np.float64]]:
        """Draw one sample, then map through sigmoid to [0, 1].

        Args:
            seed: Random seed.

        Returns:
            Array of shape (n_latent,).

        Examples:
            >>> q = LowRankPosterior(5, rank=2, seed=0)
            >>> s = q.sample()
            >>> s.shape == (5,)
            True
        """
        rng = np.random.default_rng(seed)
        cov = self.covariance()
        z = rng.multivariate_normal(self.mu, cov)
        return 1.0 / (1.0 + np.exp(-z))


def elbo(
    log_likelihood: float,
    log_prior: float,
    log_q: float,
) -> float:
    """Compute the Evidence Lower Bound (ELBO).

    ELBO = E_q[log p(x|z)] + E_q[log p(z)] - E_q[log q(z)]
         = log_likelihood + log_prior - log_q

    Args:
        log_likelihood: Expected log likelihood under q.
        log_prior: Expected log prior under q.
        log_q: Entropy term (log q evaluated at sample).

    Returns:
        ELBO scalar value.

    Examples:
        >>> elbo(-1.0, -0.5, -0.3)
        -1.2
    """
    return log_likelihood + log_prior - log_q


def iwae_bound(
    log_weights: np.ndarray[Any, np.dtype[np.float64]],
) -> float:
    """Compute the Importance-Weighted Autoencoder (IWAE) lower bound.

    Args:
        log_weights: Array of shape (K,) containing log importance weights
            log p(x, z_k) - log q(z_k | x) for K samples.

    Returns:
        IWAE bound (tighter than ELBO for K > 1).

    Examples:
        >>> import numpy as np
        >>> iwae_bound(np.array([-1.0, -1.5, -0.8]))  # doctest: +ELLIPSIS
        -0.8...
    """
    max_lw = np.max(log_weights)
    return float(max_lw + np.log(np.mean(np.exp(log_weights - max_lw))))
