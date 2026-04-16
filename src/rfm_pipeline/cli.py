from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .benchmark import run_kmeans_benchmark
from .cleaning import clean_transactions
from .config import RFMConfig, load_config
from .eda import generate_eda_report
from .efficiency import EfficiencyTracker
from .evaluation import aggregate_evaluation
from .features import build_rfm_features
from .ingestion import ingest_raw
from .manual_baseline import run_manual_baseline
from .reproducibility import run_repeated_pipeline
from .segmentation import segment_customers
from .traceability import write_traceability_manifest
from .validation import validate_online_retail


def _dirs(config: RFMConfig, run_subdir: str | None) -> tuple[Path, Path]:
    processed = config.paths.processed_dir / run_subdir if run_subdir else config.paths.processed_dir
    reports = config.paths.reports_dir / run_subdir if run_subdir else config.paths.reports_dir
    processed.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    return processed, reports


def run_pipeline(config_path: str = "configs/rfm.yaml", run_subdir: str | None = None) -> dict:
    config = load_config(config_path)
    processed_dir, report_dir = _dirs(config, run_subdir)
    tracker = EfficiencyTracker()

    with tracker.stage("ingestion"):
        raw_metadata = ingest_raw(config, report_dir)
        raw_df = pd.read_csv(config.paths.source_csv, encoding_errors="replace")
    with tracker.stage("eda"):
        eda_report = generate_eda_report(raw_df, config, report_dir)
    with tracker.stage("validation"):
        validation_report = validate_online_retail(raw_df, config, report_dir)
    with tracker.stage("cleaning"):
        cleaned, cleaning_report = clean_transactions(raw_df, config, processed_dir, report_dir)
    with tracker.stage("features"):
        rfm, rfm_metadata = build_rfm_features(cleaned, config, processed_dir, report_dir)
    with tracker.stage("segmentation"):
        segments, segment_report = segment_customers(rfm, config, processed_dir, report_dir)
    with tracker.stage("benchmark"):
        benchmark_report = run_kmeans_benchmark(rfm, config, report_dir)
    with tracker.stage("manual_baseline"):
        manual_report = run_manual_baseline(raw_df, segments, config, processed_dir, report_dir)

    efficiency_report = tracker.report(rows_processed=len(raw_df), report_dir=report_dir)
    artifact_paths = [
        report_dir / "eda_report.json",
        report_dir / "validation_report.json",
        cleaning_report["clean_dataset_path"],
        rfm_metadata["rfm_path"],
        segment_report["segments_path"],
        report_dir / "benchmark_kmeans.json",
        report_dir / "manual_comparison.json",
        report_dir / "efficiency_report.json",
    ]
    traceability_report = write_traceability_manifest(config, artifact_paths, report_dir)
    evaluation_report = aggregate_evaluation(
        report_dir,
        efficiency=efficiency_report,
        traceability=traceability_report,
        manual_comparison=manual_report,
        benchmark=benchmark_report,
    )
    return {
        "raw_metadata": raw_metadata,
        "eda": eda_report,
        "validation": validation_report,
        "evaluation": evaluation_report,
        "artifacts": {
            "segments_path": segment_report["segments_path"],
            "reports_dir": str(report_dir),
            "processed_dir": str(processed_dir),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="RFM Online Retail pipeline")
    parser.add_argument("command", choices=["run", "eda", "evaluate", "reproducibility", "manual-baseline"])
    parser.add_argument("--config", default="configs/rfm.yaml")
    parser.add_argument("--runs", type=int, default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    if args.command in {"run", "eda", "evaluate", "manual-baseline"}:
        result = run_pipeline(args.config)
        print(result["artifacts"])
        return
    if args.command == "reproducibility":
        n_runs = args.runs or config.evaluation.n_reproducibility_runs
        report = run_repeated_pipeline(lambda subdir: run_pipeline(args.config, subdir), n_runs, config.paths.reports_dir)
        print(report)


if __name__ == "__main__":
    main()
