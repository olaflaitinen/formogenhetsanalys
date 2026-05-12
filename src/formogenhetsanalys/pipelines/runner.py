"""Pipeline runner composing all estimation stages."""

from __future__ import annotations

import hashlib
from typing import Any

import polars as pl

from formogenhetsanalys.config import Config
from formogenhetsanalys.logging import get_logger
from formogenhetsanalys.paths import SYNTHETIC_ROOT
from formogenhetsanalys.seeds import set_global_seed

log = get_logger(__name__)


class Pipeline:
    """Full Förmögenhetsanalys estimation pipeline.

    Composes: ingest -> build-graph -> valuation -> train -> evaluate ->
    top-shares -> decompose -> report.

    Args:
        config: Pipeline configuration.

    Examples:
        >>> from formogenhetsanalys.config import Config
        >>> import pathlib
        >>> cfg = Config(data_root=pathlib.Path("data"))
        >>> p = Pipeline(cfg)
        >>> p is not None
        True
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        set_global_seed(config.seed)

    def run_synthetic(self) -> dict[str, Any]:
        """Execute the full pipeline on the synthetic graph fixture.

        Returns:
            Dict with keys 'top_shares', 'gini', 'decomposition', 'receipt_sha256'.

        Examples:
            >>> from formogenhetsanalys.config import Config
            >>> import pathlib
            >>> cfg = Config(data_root=pathlib.Path("data"))
            >>> p = Pipeline(cfg)
            >>> result = p.run_synthetic()
            >>> "top_shares" in result
            True
        """
        from formogenhetsanalys.estimation.decomposition import atkinson, gini, theil
        from formogenhetsanalys.estimation.top_shares import top_shares_bootstrap
        from formogenhetsanalys.ingestion.firm_register import synthetic_firm_register
        from formogenhetsanalys.ingestion.wealth_register import synthetic_wealth_register
        from formogenhetsanalys.valuation.harmonisation import harmonise_valuations

        log.info("pipeline.run_synthetic", seed=self.config.seed)

        hh_df = synthetic_wealth_register(n=1000, seed=self.config.seed)
        firm_df = synthetic_firm_register(n=200, seed=self.config.seed)

        harmonised = harmonise_valuations(hh_df, firm_df, method=self.config.valuation)
        wealth = harmonised["harmonised_wealth"].to_numpy(allow_copy=True)

        ts = top_shares_bootstrap(wealth, [0.99, 0.999], n_boot=100, seed=7)
        gini_val = gini(wealth)
        atk_val = atkinson(wealth, 0.5)
        theil_val = theil(wealth)

        result: dict[str, Any] = {
            "top_shares": ts,
            "gini": gini_val,
            "atkinson": atk_val,
            "theil": theil_val,
            "decomposition": {"gini": gini_val, "atkinson": atk_val, "theil": theil_val},
        }

        receipt = str(sorted(str(v) for v in result.items()))
        result["receipt_sha256"] = hashlib.sha256(receipt.encode()).hexdigest()

        log.info("pipeline.complete", receipt=result["receipt_sha256"])
        return result

    def load_synthetic_parquet(self) -> pl.DataFrame | None:
        """Load households from the synthetic Parquet fixture if it exists.

        Returns:
            Polars DataFrame or None if fixtures not yet generated.

        Examples:
            >>> from formogenhetsanalys.config import Config
            >>> import pathlib
            >>> cfg = Config(data_root=pathlib.Path("data"))
            >>> p = Pipeline(cfg)
            >>> df = p.load_synthetic_parquet()
        """
        parquet_path = SYNTHETIC_ROOT / "households.parquet"
        if parquet_path.exists():
            return pl.read_parquet(parquet_path)
        return None
