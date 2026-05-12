"""Negative-edge sampling for link-prediction objectives."""

from __future__ import annotations

from typing import Any

import numpy as np


def sample_negative_edges(
    edge_index: tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]],
    num_nodes_src: int,
    num_nodes_dst: int,
    num_neg: int | None = None,
    seed: int = 20251008,
) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
    """Sample negative (non-existent) edges for link-prediction training.

    Uses a corruption strategy: for each positive edge, sample one random
    destination node that does not appear as a true destination for the same
    source.

    Args:
        edge_index: Tuple of (src, dst) arrays for positive edges.
        num_nodes_src: Total number of source nodes.
        num_nodes_dst: Total number of destination nodes.
        num_neg: Number of negative edges to sample; defaults to len(positive edges).
        seed: Random seed.

    Returns:
        Tuple of (neg_src, neg_dst) arrays.

    Examples:
        >>> import numpy as np
        >>> src = np.array([0, 1, 2])
        >>> dst = np.array([0, 1, 2])
        >>> ns, nd = sample_negative_edges((src, dst), 5, 5, seed=42)
        >>> len(ns) == len(src)
        True
    """
    rng = np.random.default_rng(seed)
    pos_src, pos_dst = edge_index
    n_pos = len(pos_src)
    n_neg = num_neg if num_neg is not None else n_pos

    pos_set = set(zip(pos_src.tolist(), pos_dst.tolist(), strict=False))

    neg_src_list: list[int] = []
    neg_dst_list: list[int] = []
    attempts = 0
    max_attempts = n_neg * 20

    while len(neg_src_list) < n_neg and attempts < max_attempts:
        s = int(rng.integers(0, num_nodes_src))
        d = int(rng.integers(0, num_nodes_dst))
        if (s, d) not in pos_set:
            neg_src_list.append(s)
            neg_dst_list.append(d)
        attempts += 1

    return (
        np.array(neg_src_list, dtype=np.int64),
        np.array(neg_dst_list, dtype=np.int64),
    )


def corrupt_edges(
    edge_index: tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]],
    num_nodes_dst: int,
    seed: int = 20251008,
) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
    """Corrupt positive edges by replacing destinations with random nodes.

    Args:
        edge_index: Tuple of (src, dst) arrays.
        num_nodes_dst: Number of destination nodes to sample from.
        seed: Random seed.

    Returns:
        Tuple of (src, corrupted_dst) arrays with the same length as input.

    Examples:
        >>> import numpy as np
        >>> src = np.array([0, 1, 2])
        >>> dst = np.array([3, 4, 5])
        >>> cs, cd = corrupt_edges((src, dst), 10, seed=42)
        >>> len(cs) == 3
        True
    """
    rng = np.random.default_rng(seed)
    pos_src, _ = edge_index
    corrupted_dst = rng.integers(0, num_nodes_dst, size=len(pos_src)).astype(np.int64)
    return pos_src.copy(), corrupted_dst
