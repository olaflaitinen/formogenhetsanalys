"""Generate synthetic graph data for testing and demonstration."""

from __future__ import annotations

import hashlib
import json
import pathlib

from formogenhetsanalys.ingestion.firm_register import synthetic_firm_register
from formogenhetsanalys.ingestion.wealth_register import synthetic_wealth_register

SYNTHETIC_SEED = 19960307


def compute_receipt(data: bytes) -> str:
    """Compute SHA256 receipt for data."""
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def main() -> None:
    """Generate all synthetic data files."""
    import numpy as np
    import polars as pl

    data_dir = pathlib.Path("data/synthetic")
    data_dir.mkdir(parents=True, exist_ok=True)

    receipts = {}

    # Generate households
    households_df = synthetic_wealth_register(n=200, seed=SYNTHETIC_SEED)
    households_path = data_dir / "households.parquet"
    households_df.write_parquet(households_path)
    with open(households_path, "rb") as f:
        receipts["synthetic_households"] = compute_receipt(f.read())

    # Generate firms
    firms_df = synthetic_firm_register(n=50, seed=SYNTHETIC_SEED)
    firms_path = data_dir / "firms.parquet"
    firms_df.write_parquet(firms_path)
    with open(firms_path, "rb") as f:
        receipts["synthetic_firms"] = compute_receipt(f.read())

    # Generate assets
    rng = np.random.default_rng(SYNTHETIC_SEED + 2)
    assets_df = pl.DataFrame(
        {
            "asset_id": [f"A{i:04d}" for i in range(100)],
            "asset_type": rng.choice(["real_estate", "listed_equity"], 100),
            "value_market": rng.lognormal(13.0, 2.0, 100),
            "value_book": rng.lognormal(12.5, 1.8, 100),
            "isin": [""] * 100,
            "year": [2022] * 100,
        }
    )
    assets_path = data_dir / "assets.parquet"
    assets_df.write_parquet(assets_path)
    with open(assets_path, "rb") as f:
        receipts["synthetic_assets"] = compute_receipt(f.read())

    # Generate ownership edges
    hh_ids = households_df["household_id"].to_list()
    firm_ids = firms_df["firm_id"].to_list()
    asset_ids = assets_df["asset_id"].to_list()
    n_edges = 300
    edges_ownership = pl.DataFrame(
        {
            "source_id": rng.choice(hh_ids + firm_ids, n_edges),
            "target_id": rng.choice(firm_ids + asset_ids, n_edges),
            "ownership_share": rng.dirichlet(np.ones(n_edges), size=1)[0],
            "ownership_type": rng.choice(["direct", "indirect"], n_edges),
            "year": [2022] * n_edges,
        }
    )
    ownership_path = data_dir / "edges_ownership.parquet"
    edges_ownership.write_parquet(ownership_path)
    with open(ownership_path, "rb") as f:
        receipts["synthetic_ownership"] = compute_receipt(f.read())

    # Generate kinship edges
    kinship_df = pl.DataFrame(
        {
            "source_id": rng.choice(hh_ids, 50),
            "target_id": rng.choice(hh_ids, 50),
            "kinship_type": rng.choice(["spouse", "parent-child", "sibling"], 50),
            "year": [2022] * 50,
        }
    )
    kinship_path = data_dir / "edges_kinship.parquet"
    kinship_df.write_parquet(kinship_path)
    with open(kinship_path, "rb") as f:
        receipts["synthetic_kinship"] = compute_receipt(f.read())

    # Save receipts
    receipts_path = pathlib.Path("replication/receipts.json")
    receipts_path.parent.mkdir(parents=True, exist_ok=True)
    with open(receipts_path, "w") as f:
        json.dump(receipts, f, indent=2)

    print("Synthetic data generated successfully.")
    print(f"Households: {len(households_df)} rows")
    print(f"Firms: {len(firms_df)} rows")
    print(f"Assets: {len(assets_df)} rows")
    print(f"Ownership edges: {len(edges_ownership)} rows")
    print(f"Kinship edges: {len(kinship_df)} rows")
    print(f"Receipts saved to {receipts_path}")


if __name__ == "__main__":
    main()
