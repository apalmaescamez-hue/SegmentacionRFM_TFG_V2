from __future__ import annotations

import json
import uuid
from pathlib import Path

import pandas as pd

from rfm_pipeline.cleaning import clean_transactions
from rfm_pipeline.config import CleaningConfig, EvaluationConfig, PathsConfig, PipelineConfig, RFMConfig
from rfm_pipeline.evaluation import aggregate_evaluation
from rfm_pipeline.features import build_rfm_features
from rfm_pipeline.io import write_dataframe
from rfm_pipeline.reproducibility import compare_segment_outputs
from rfm_pipeline.segmentation import segment_customers, stable_quantile_score
from rfm_pipeline.validation import validate_online_retail


SEGMENTS = {
    "champions": "Champions",
    "loyal": "Loyal Customers",
    "potential": "Potential Loyalists",
    "new": "New Customers",
    "need_attention": "Need Attention",
    "at_risk": "At Risk",
    "cannot_lose": "Cannot Lose Them",
    "hibernating": "Hibernating",
    "others": "Others",
}


def make_test_dir() -> Path:
    path = Path("tests_tmp") / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=True)
    return path


def make_config(tmp_path: Path) -> RFMConfig:
    return RFMConfig(
        paths=PathsConfig(
            source_csv=tmp_path / "raw.csv",
            raw_dir=tmp_path / "raw",
            interim_dir=tmp_path / "interim",
            processed_dir=tmp_path / "processed",
            reports_dir=tmp_path / "reports",
        ),
        pipeline=PipelineConfig(snapshot_date="2011-12-10", rfm_bins=5),
        cleaning=CleaningConfig(),
        evaluation=EvaluationConfig(n_reproducibility_runs=3),
        segments=SEGMENTS,
    )


def sample_raw_transactions() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["1", "A", "Product A", 2, "2011-12-01 10:00:00", 10.0, 10001.0, "United Kingdom"],
            ["2", "B", "Product B", 1, "2011-12-03 11:00:00", 20.0, 10001.0, "United Kingdom"],
            ["3", "C", "Product C", 3, "2011-12-05 12:00:00", 15.0, 10002.0, "Spain"],
            ["C4", "D", "Cancelled", -1, "2011-12-06 13:00:00", 8.0, 10003.0, "France"],
            ["5", "E", "Missing customer", 1, "2011-12-07 14:00:00", 9.0, None, "Germany"],
            ["6", "F", "Free item", 1, "2011-12-08 15:00:00", 0.0, 10004.0, "Italy"],
        ],
        columns=[
            "InvoiceNo",
            "StockCode",
            "Description",
            "Quantity",
            "InvoiceDate",
            "UnitPrice",
            "CustomerID",
            "Country",
        ],
    )


def test_validation_report_passes_valid_online_retail_schema() -> None:
    workdir = make_test_dir()
    config = make_config(workdir)
    report = validate_online_retail(sample_raw_transactions(), config, workdir / "reports")

    assert report["passed"] is True
    assert report["missing_columns"] == []
    assert report["type_checks"]["InvoiceDate_parseable_ratio"] == 1.0
    assert (workdir / "reports" / "validation_report.json").exists()


def test_cleaning_removes_invalid_rows_and_normalizes_customer_id() -> None:
    workdir = make_test_dir()
    config = make_config(workdir)
    cleaned, report = clean_transactions(sample_raw_transactions(), config, workdir / "processed", workdir / "reports")

    assert len(cleaned) == 3
    assert report["initial_rows"] == 6
    assert set(cleaned["CustomerID"]) == {"10001", "10002"}
    assert not cleaned["InvoiceNo"].astype(str).str.startswith("C").any()
    assert (cleaned["Quantity"] > 0).all()
    assert (cleaned["UnitPrice"] > 0).all()


def test_build_rfm_features_uses_snapshot_date_and_customer_aggregation() -> None:
    workdir = make_test_dir()
    config = make_config(workdir)
    cleaned, _ = clean_transactions(sample_raw_transactions(), config, workdir / "processed", workdir / "reports")
    rfm, metadata = build_rfm_features(cleaned, config, workdir / "processed", workdir / "reports")

    customer = rfm.loc[rfm["customer_id"] == "10001"].iloc[0]
    assert customer["frequency"] == 2
    assert customer["monetary"] == 40.0
    assert customer["recency"] == 6
    assert metadata["customers"] == 2


def test_segment_scores_are_stable_and_within_configured_range() -> None:
    workdir = make_test_dir()
    config = make_config(workdir)
    rfm = pd.DataFrame(
        {
            "customer_id": [str(i) for i in range(1, 11)],
            "recency": [1, 3, 7, 10, 15, 20, 35, 60, 90, 120],
            "frequency": [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
            "monetary": [1000, 900, 800, 700, 600, 500, 400, 300, 200, 100],
        }
    )

    segments, report = segment_customers(rfm, config, workdir / "processed", workdir / "reports")

    for column in ["r_score", "f_score", "m_score"]:
        assert segments[column].between(1, 5).all()
    assert segments["segment"].notna().all()
    assert report["customers"] == 10
    assert stable_quantile_score(pd.Series([1, 2, 3, 4, 5]), bins=5).tolist() == [1, 2, 3, 4, 5]


def test_reproducibility_report_detects_identical_segment_outputs() -> None:
    workdir = make_test_dir()
    frame = pd.DataFrame(
        {
            "customer_id": ["1", "2"],
            "recency": [1, 2],
            "frequency": [3, 4],
            "monetary": [100.0, 200.0],
            "segment": ["Champions", "Loyal Customers"],
        }
    )
    first = write_dataframe(frame, workdir / "run1" / "segments.parquet")
    second = write_dataframe(frame.copy(), workdir / "run2" / "segments.parquet")

    report = compare_segment_outputs([first, second], workdir / "reports")

    assert report["runs"] == 2
    assert report["output_hash_match_rate"] == 1.0
    assert report["segment_stability"] == 1.0
    assert report["rfm_numeric_delta_max"] == 0.0


def test_evaluation_report_persists_reproducibility_payload() -> None:
    workdir = make_test_dir()
    reproducibility = {"runs": 3, "output_hash_match_rate": 1.0}

    payload = aggregate_evaluation(workdir, reproducibility=reproducibility, efficiency={"total_runtime_seconds": 1.2})
    saved = json.loads((workdir / "evaluation_report.json").read_text(encoding="utf-8"))

    assert payload["reproducibility"] == reproducibility
    assert saved["reproducibility"]["runs"] == 3
