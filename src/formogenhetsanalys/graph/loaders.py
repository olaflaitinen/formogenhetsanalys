"""Neighbour samplers, mini-batch construction, and train/val/test splits."""

from __future__ import annotations

from typing import Any

import numpy as np


def train_val_test_split(
    n: int,
    train_frac: float = 0.7,
    val_frac: float = 0.15,
    seed: int = 20251008,
) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any], np.ndarray[Any, Any]]:
    """Split node indices into train, validation, and test sets.

    Args:
        n: Total number of nodes.
        train_frac: Fraction for training.
        val_frac: Fraction for validation. Test fraction is 1 - train - val.
        seed: Random seed for the split.

    Returns:
        Three numpy arrays of integer indices: (train_idx, val_idx, test_idx).

    Examples:
        >>> tr, va, te = train_val_test_split(100, seed=42)
        >>> len(tr) + len(va) + len(te) == 100
        True
    """
    rng = np.random.default_rng(seed)
    idx = rng.permutation(n)
    n_train = int(n * train_frac)
    n_val = int(n * val_frac)
    return idx[:n_train], idx[n_train : n_train + n_val], idx[n_train + n_val :]


def make_mini_batches(
    indices: np.ndarray[Any, Any],
    batch_size: int = 256,
    shuffle: bool = True,
    seed: int = 20251008,
) -> list[np.ndarray[Any, Any]]:
    """Partition node indices into mini-batches.

    Args:
        indices: Array of node indices to partition.
        batch_size: Number of nodes per batch.
        shuffle: Whether to shuffle before splitting.
        seed: Random seed used when shuffle is True.

    Returns:
        List of numpy arrays, each of length at most batch_size.

    Examples:
        >>> import numpy as np
        >>> idx = np.arange(100)
        >>> batches = make_mini_batches(idx, batch_size=32, shuffle=False)
        >>> len(batches)
        4
    """
    if shuffle:
        rng = np.random.default_rng(seed)
        indices = rng.permutation(indices)

    return [indices[i : i + batch_size] for i in range(0, len(indices), batch_size)]


def sample_neighbours(
    edge_index: Any,
    node_idx: np.ndarray[Any, Any],
    num_neighbours: int = 10,
    seed: int = 20251008,
) -> Any:
    """Sample a fixed number of neighbours for each node in node_idx.

    Falls back to a simple numpy implementation when PyTorch Geometric is
    not available.

    Args:
        edge_index: Edge index tensor or (src, dst) tuple of arrays.
        node_idx: Indices of nodes for which to sample neighbours.
        num_neighbours: Maximum neighbours to sample per node.
        seed: Random seed.

    Returns:
        Sampled edge index covering node_idx and their sampled neighbours.

    Examples:
        >>> import numpy as np
        >>> ei = (np.array([0, 1, 2, 0]), np.array([1, 2, 3, 3]))
        >>> result = sample_neighbours(ei, np.array([0, 1]), num_neighbours=2, seed=42)
        >>> result is not None
        True
    """
    rng = np.random.default_rng(seed)

    if isinstance(edge_index, tuple):
        src_arr, dst_arr = edge_index
    else:
        try:
            src_arr = edge_index[0].numpy()
            dst_arr = edge_index[1].numpy()
        except AttributeError:
            src_arr = np.asarray(edge_index[0])
            dst_arr = np.asarray(edge_index[1])

    node_set = set(node_idx.tolist())
    sampled_src: list[int] = []
    sampled_dst: list[int] = []

    for node in node_idx:
        mask = dst_arr == node
        neighbours = src_arr[mask]
        if len(neighbours) > num_neighbours:
            chosen = rng.choice(neighbours, size=num_neighbours, replace=False)
        else:
            chosen = neighbours
        for nb in chosen:
            sampled_src.append(int(nb))
            sampled_dst.append(int(node))
            node_set.add(int(nb))

    return (np.array(sampled_src, dtype=np.int64), np.array(sampled_dst, dtype=np.int64))
