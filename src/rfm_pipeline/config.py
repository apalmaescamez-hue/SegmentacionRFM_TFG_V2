from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class PathsConfig(BaseModel):
    source_csv: Path
    raw_dir: Path = Path("data/raw")
    interim_dir: Path = Path("data/interim")
    processed_dir: Path = Path("data/processed")
    reports_dir: Path = Path("reports")


class PipelineConfig(BaseModel):
    snapshot_strategy: str = "max_invoice_date_plus_one_day"
    snapshot_date: Optional[str] = None
    rfm_bins: int = Field(default=5, ge=2, le=10)
    rules_version: str = "rfm_rules_v1"
    thresholds_version: str = "thresholds_v1"


class CleaningConfig(BaseModel):
    drop_missing_customer_id: bool = True
    exclude_cancelled_invoices: bool = True
    require_positive_quantity: bool = True
    require_positive_unit_price: bool = True
    drop_exact_duplicates: bool = True


class EvaluationConfig(BaseModel):
    n_reproducibility_runs: int = Field(default=3, ge=2, le=20)
    manual_baseline_name: str = "excel_style_manual_baseline"


class RFMConfig(BaseModel):
    paths: PathsConfig
    pipeline: PipelineConfig = PipelineConfig()
    cleaning: CleaningConfig = CleaningConfig()
    evaluation: EvaluationConfig = EvaluationConfig()
    segments: dict[str, str]

    def ensure_directories(self) -> None:
        for path in [
            self.paths.raw_dir,
            self.paths.interim_dir,
            self.paths.processed_dir,
            self.paths.reports_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)


def load_config(path: str | Path = "configs/rfm.yaml") -> RFMConfig:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    config = RFMConfig.model_validate(raw)
    config.ensure_directories()
    return config
