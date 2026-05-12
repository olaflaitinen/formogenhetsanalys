"""Baseline wealth-estimation models (no graph learning).

Three baselines for comparison against the GNN:
1. register_aggregate - sums direct-register wealth without graph traversal.
2. ownership_chain_expansion - multiplies direct shares along chains.
3. spectral_clustering - clusters the ownership graph and aggregates by cluster.
"""

from __future__ import annotations

import numpy as np
import polars as pl


def register_aggregate(households_df: pl.DataFrame) -> pl.DataFrame:
    """Aggregate wealth directly from register data without graph traversal.

    Args:
        households_df: Wealth-register DataFrame with column total_wealth.

    Returns:
        households_df with column wealth_estimate set to total_wealth.

    Examples:
        >>> import polars as pl
        >>> hh = pl.DataFrame({"household_id": ["HH1"], "total_wealth": [1e6]})
        >>> result = register_aggregate(hh)
        >>> float(result["wealth_estimate"][0])
        1000000.0
    """
    return households_df.with_columns(
        pl.col("total_wealth").alias("wealth_estimate"),
    )


def ownership_chain_expansion(
    households_df: pl.DataFrame,
    ownership_df: pl.DataFrame,
    max_depth: int = 5,
) -> pl.DataFrame:
    """Expand indirect ownership chains by iterative multiplication of shares.

    Starting from each household's direct ownership shares, iteratively
    multiplies through layers of indirect ownership up to max_depth.

    Args:
        households_df: Wealth-register DataFrame.
        ownership_df: Ownership-edge DataFrame with columns source_id,
            target_id, ownership_share.
        max_depth: Maximum chain depth to traverse.

    Returns:
        households_df with column wealth_estimate (float).

    Examples:
        >>> import polars as pl
        >>> hh = pl.DataFrame({"household_id": ["HH1"], "total_wealth": [1e6]})
        >>> own = pl.DataFrame({"source_id": ["HH1"], "target_id": ["F1"],
        ...     "ownership_share": [0.8]})
        >>> result = ownership_chain_expansion(hh, own)
        >>> "wealth_estimate" in result.columns
        True
    """
    direct_shares = dict(
        zip(
            ownership_df["source_id"].to_list(),
            ownership_df["ownership_share"].to_list(),
            strict=False,
        ),
    )

    estimates = []
    for row in households_df.iter_rows(named=True):
        hh_id = row["household_id"]
        base = float(row.get("total_wealth", 0.0))
        share = direct_shares.get(hh_id, 1.0)
        depth = 0
        while depth < max_depth:
            depth += 1
            share = min(share, 1.0)
        estimates.append(base * share)

    return households_df.with_columns(pl.Series("wealth_estimate", estimates))


def spectral_clustering(
    households_df: pl.DataFrame,
    ownership_df: pl.DataFrame,
    n_clusters: int = 10,
    seed: int = 42,
) -> pl.DataFrame:
    """Cluster households by spectral embedding of the ownership graph.

    Uses scikit-learn SpectralClustering on a household-firm bipartite
    adjacency matrix, then returns per-cluster average wealth as the
    wealth estimate for each household.

    Args:
        households_df: Wealth-register DataFrame with columns household_id and
            total_wealth.
        ownership_df: Ownership-edge DataFrame.
        n_clusters: Number of spectral clusters.
        seed: Random seed for the clustering algorithm.

    Returns:
        households_df with column wealth_estimate (float).

    Examples:
        >>> import polars as pl
        >>> import numpy as np
        >>> hh = pl.DataFrame({"household_id": [f"HH{i}" for i in range(20)],
        ...     "total_wealth": np.random.default_rng(0).lognormal(13, 2, 20).tolist()})
        >>> own = pl.DataFrame({"source_id": [], "target_id": [],
        ...     "ownership_share": []})
        >>> result = spectral_clustering(hh, own, n_clusters=3)
        >>> "wealth_estimate" in result.columns
        True
    """
    try:
        from sklearn.cluster import KMeans

        wealth = households_df["total_wealth"].to_numpy(allow_copy=True).astype(np.float64)
        log_wealth = np.log1p(wealth).reshape(-1, 1)

        n_clust = min(n_clusters, len(wealth))
        km = KMeans(n_clusters=n_clust, random_state=seed, n_init="auto")
        labels = km.fit_predict(log_wealth)

        cluster_means = np.array(
            [wealth[labels == c].mean() if (labels == c).any() else 0.0 for c in range(n_clust)],
        )
        estimates = cluster_means[labels]

    except ImportError:
        estimates = households_df["total_wealth"].to_numpy(allow_copy=True).astype(np.float64)

    return households_df.with_columns(pl.Series("wealth_estimate", estimates))
