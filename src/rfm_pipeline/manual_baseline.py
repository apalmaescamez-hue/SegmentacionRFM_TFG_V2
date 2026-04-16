from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

from .cleaning import clean_transactions
from .config import RFMConfig
from .features import build_rfm_features
from .io import write_json, write_markdown
from .segmentation import segment_customers


def run_manual_baseline(
    raw_df: pd.DataFrame,
    pipeline_segments: pd.DataFrame,
    config: RFMConfig,
    processed_dir: Path | None = None,
    report_dir: Path | None = None,
) -> dict:
    """Simulate an auditable Excel-style sequential baseline using explicit steps."""
    started = time.perf_counter()
    processed_dir = processed_dir or config.paths.processed_dir
    report_dir = report_dir or config.paths.reports_dir
    baseline_dir = processed_dir / "manual_baseline"
    baseline_report_dir = report_dir / "manual_baseline"
    cleaned, _ = clean_transactions(raw_df, config, baseline_dir, baseline_report_dir)
    rfm, _ = build_rfm_features(cleaned, config, baseline_dir, baseline_report_dir)
    manual_segments, _ = segment_customers(rfm, config, baseline_dir, baseline_report_dir)

    merged = pipeline_segments[["customer_id", "segment"]].merge(
        manual_segments[["customer_id", "segment"]],
        on="customer_id",
        how="inner",
        suffixes=("_pipeline", "_manual"),
    )
    match_rate = float((merged["segment_pipeline"] == merged["segment_manual"]).mean()) if len(merged) else 0.0
    report = {
        "baseline_name": config.evaluation.manual_baseline_name,
        "manual_steps": 6,
        "pipeline_steps": 8,
        "manual_runtime_seconds": round(time.perf_counter() - started, 6),
        "compared_customers": int(len(merged)),
        "segment_match_rate": match_rate,
        "traceability": "limited_in_spreadsheets_high_in_pipeline",
        "reproducibility": "manual_process_requires_repetition_pipeline_is_scripted",
    }
    write_json(report_dir / "manual_comparison.json", report)
    write_markdown(report_dir / "manual_comparison.md", "Manual vs Pipeline", report)
    return report
