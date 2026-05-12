"""Heterogeneous graph builder.

Converts tabular register data into a torch_geometric.data.HeteroData object
that the GNN models consume.  When PyTorch Geometric is not installed the
builder returns a lightweight dict-based stub so that the rest of the pipeline
can still be tested without the heavy ML dependencies.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import polars as pl


def _to_float_tensor(arr: np.ndarray[Any, Any]) -> Any:
    """Convert a numpy array to a float32 torch tensor if torch is available."""
    try:
        import torch

        return torch.tensor(arr, dtype=torch.float32)
    except ImportError:
        return arr.astype(np.float32)


def _to_long_tensor(arr: np.ndarray[Any, Any]) -> Any:
    """Convert a numpy array to a long torch tensor if torch is available."""
    try:
        import torch

        return torch.tensor(arr, dtype=torch.long)
    except ImportError:
        return arr.astype(np.int64)


def build_graph(
    households_df: pl.DataFrame,
    firms_df: pl.DataFrame,
    assets_df: pl.DataFrame,
    ownership_df: pl.DataFrame,
    kinship_df: pl.DataFrame | None = None,
    individuals_df: pl.DataFrame | None = None,
) -> Any:
    """Build a heterogeneous ownership graph from register DataFrames.

    Returns a torch_geometric.data.HeteroData when PyTorch Geometric is
    available, otherwise returns a plain dict with the same structure.

    Args:
        households_df: Wealth-register DataFrame with household nodes.
        firms_df: Firm-register DataFrame with firm nodes.
        assets_df: Asset DataFrame with asset nodes.
        ownership_df: Ownership-edge DataFrame with columns source_id,
            target_id, ownership_share, source_type, target_type.
        kinship_df: Optional kinship-edge DataFrame.
        individuals_df: Optional individual-node DataFrame.

    Returns:
        HeteroData (or dict stub) with node feature matrices x and edge
        index tensors for each (src_type, rel_type, dst_type) triple.

    Examples:
        >>> import polars as pl
        >>> hh = pl.DataFrame({"household_id": ["HH1"], "total_wealth": [1e6],
        ...     "financial_wealth": [3e5], "real_estate_wealth": [5e5],
        ...     "business_wealth": [2e5], "debt": [1e5]})
        >>> firms = pl.DataFrame({"firm_id": ["F1"], "equity_book": [1e5],
        ...     "revenue": [5e4], "profit": [1e4]})
        >>> assets = pl.DataFrame({"asset_id": ["A1"], "value_market": [2e4],
        ...     "value_book": [1.8e4]})
        >>> own = pl.DataFrame({"source_id": ["HH1"], "target_id": ["F1"],
        ...     "ownership_share": [1.0], "source_type": ["household"],
        ...     "target_type": ["firm"]})
        >>> g = build_graph(hh, firms, assets, own)
        >>> g is not None
        True
    """
    hh_ids = {v: i for i, v in enumerate(households_df["household_id"].to_list())}
    firm_ids = {v: i for i, v in enumerate(firms_df["firm_id"].to_list())}
    asset_ids = {v: i for i, v in enumerate(assets_df["asset_id"].to_list())}

    wealth_cols = [
        "total_wealth",
        "financial_wealth",
        "real_estate_wealth",
        "business_wealth",
        "debt",
    ]
    hh_feats = (
        households_df.select(
            [c for c in wealth_cols if c in households_df.columns],
        )
        .to_numpy()
        .astype(np.float32)
    )

    firm_feat_cols = [c for c in ["equity_book", "revenue", "profit"] if c in firms_df.columns]
    firm_feats = firms_df.select(firm_feat_cols).to_numpy().astype(np.float32)

    asset_feat_cols = [c for c in ["value_market", "value_book"] if c in assets_df.columns]
    asset_feats = assets_df.select(asset_feat_cols).to_numpy().astype(np.float32)

    id_maps: dict[str, dict[str, int]] = {
        "household": hh_ids,
        "firm": firm_ids,
        "asset": asset_ids,
    }

    edge_index_dict: dict[tuple[str, str, str], tuple[list[int], list[int]]] = {}

    for row in ownership_df.iter_rows(named=True):
        src_type = str(row.get("source_type", "household"))
        dst_type = str(row.get("target_type", "firm"))
        src_map = id_maps.get(src_type, {})
        dst_map = id_maps.get(dst_type, {})
        src_idx = src_map.get(str(row["source_id"]), -1)
        dst_idx = dst_map.get(str(row["target_id"]), -1)
        if src_idx < 0 or dst_idx < 0:
            continue
        key = (src_type, "ownership", dst_type)
        if key not in edge_index_dict:
            edge_index_dict[key] = ([], [])
        edge_index_dict[key][0].append(src_idx)
        edge_index_dict[key][1].append(dst_idx)

    if kinship_df is not None:
        ind_ids: dict[str, int] = {}
        if individuals_df is not None:
            ind_ids = {v: i for i, v in enumerate(individuals_df["individual_id"].to_list())}
        for row in kinship_df.iter_rows(named=True):
            si = ind_ids.get(str(row["source_id"]), -1)
            di = ind_ids.get(str(row["target_id"]), -1)
            if si < 0 or di < 0:
                continue
            key = ("individual", "kinship", "individual")
            if key not in edge_index_dict:
                edge_index_dict[key] = ([], [])
            edge_index_dict[key][0].append(si)
            edge_index_dict[key][1].append(di)

    try:
        from torch_geometric.data import HeteroData

        data = HeteroData()
        data["household"].x = _to_float_tensor(hh_feats)
        data["firm"].x = _to_float_tensor(firm_feats)
        data["asset"].x = _to_float_tensor(asset_feats)

        for (src, rel, dst), (srcs, dsts) in edge_index_dict.items():
            ei = np.array([srcs, dsts], dtype=np.int64)
            data[src, rel, dst].edge_index = _to_long_tensor(ei)

        return data

    except ImportError:
        stub: dict[str, Any] = {
            "node_features": {
                "household": _to_float_tensor(hh_feats),
                "firm": _to_float_tensor(firm_feats),
                "asset": _to_float_tensor(asset_feats),
            },
            "edge_index": {
                k: (np.array(v[0], dtype=np.int64), np.array(v[1], dtype=np.int64))
                for k, v in edge_index_dict.items()
            },
        }
        return stub
