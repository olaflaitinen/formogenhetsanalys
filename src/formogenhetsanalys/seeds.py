"""Reproducibility utilities: global seed management and sub-seed derivation.

All randomness in the pipeline must flow through derive_seed so that every
component is deterministically seeded from the single master seed.
"""

from __future__ import annotations

import hashlib
import os
import random

SYNTHETIC_SEED: int = 19960307
MODEL_SEED: int = 20251008
GNN_INIT_SEED: int = 42

NAMESPACES = (
    "graph_split",
    "neighbour_sampler",
    "negative_sampler",
    "variational_init",
)


def derive_seed(master: int, namespace: str) -> int:
    """Derive a deterministic child seed for a named component.

    Args:
        master: The master seed (e.g. Config.seed).
        namespace: A short ASCII label identifying the component.

    Returns:
        A non-negative integer seed suitable for seeding numpy or torch.

    Examples:
        >>> derive_seed(20251008, "graph_split")
        3722191716
    """
    digest = hashlib.sha256(f"{master}:{namespace}".encode()).digest()
    return int.from_bytes(digest[:4], "big")


def set_global_seed(seed: int) -> None:
    """Seed all random-number generators used by the pipeline.

    Sets seeds for the Python standard library, NumPy, PyTorch (including
    CUDA), and JAX. Also configures PyTorch for deterministic algorithms and
    sets CUBLAS_WORKSPACE_CONFIG for reproducible CUDA GEMM operations.

    Note:
        torch.use_deterministic_algorithms(True) may raise RuntimeError for
        some CUDA operations that lack deterministic implementations. In that
        case, fall back to torch.use_deterministic_algorithms(False, warn_only=True)
        and document the deviation in docs/reproducibility.md.

    Args:
        seed: Integer seed. Must be non-negative and fit in a 32-bit unsigned int.

    Examples:
        >>> set_global_seed(42)
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"

    random.seed(seed)

    try:
        import numpy as np

        np.random.seed(seed % (2**32))
    except ImportError:
        pass

    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        torch.use_deterministic_algorithms(True, warn_only=True)
    except ImportError:
        pass

    try:
        import jax

        jax.config.update("jax_enable_x64", True)
    except ImportError:
        pass
