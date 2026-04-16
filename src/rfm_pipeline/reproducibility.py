from __future__ import annotations

from pathlib import Path
from typing import Callable

from .io import dataframe_hash, read_dataframe, write_json, write_markdown


def compare_segment_outputs(segment_paths: list[str | Path], report_dir: Path) -> dict:
    frames = [read_dataframe(path).sort_values("customer_id").reset_index(drop=True) for path in segment_paths]
    hashes = [dataframe_hash(frame) for frame in frames]
    base = frames[0][["customer_id", "recency", "frequency", "monetary", "segment"]]
    stabilities = []
    numeric_deltas = []
    for frame in frames[1:]:
        current = frame[["customer_id", "recency", "frequency", "monetary", "segment"]]
        merged = base.merge(current, on="customer_id", suffixes=("_base", "_current"))
        stabilities.append(float((merged["segment_base"] == merged["segment_current"]).mean()))
        deltas = [
            (merged[f"{col}_base"] - merged[f"{col}_current"]).abs().max()
            for col in ["recency", "frequency", "monetary"]
        ]
        numeric_deltas.append(float(max(deltas)))
    report = {
        "runs": len(segment_paths),
        "output_hash_match_rate": float(sum(h == hashes[0] for h in hashes) / len(hashes)),
        "segment_stability": float(min(stabilities) if stabilities else 1.0),
        "rfm_numeric_delta_max": float(max(numeric_deltas) if numeric_deltas else 0.0),
        "output_hashes": hashes,
    }
    write_json(report_dir / "reproducibility_report.json", report)
    write_markdown(report_dir / "reproducibility_report.md", "Reproducibility Report", report)
    return report


def run_repeated_pipeline(pipeline_func: Callable[[str], dict], n_runs: int, report_dir: Path) -> dict:
    segment_paths = []
    for idx in range(1, n_runs + 1):
        result = pipeline_func(f"reproducibility_runs/run_{idx}")
        segment_paths.append(result["artifacts"]["segments_path"])
    return compare_segment_outputs(segment_paths, report_dir)
