from __future__ import annotations

from pathlib import Path

from .io import write_json, write_markdown


def aggregate_evaluation(
    report_dir: Path,
    *,
    reproducibility: dict | None = None,
    efficiency: dict | None = None,
    traceability: dict | None = None,
    manual_comparison: dict | None = None,
    benchmark: dict | None = None,
) -> dict:
    payload = {
        "reproducibility": reproducibility or {},
        "efficiency": efficiency or {},
        "traceability": traceability or {},
        "manual_comparison": manual_comparison or {},
        "benchmark": benchmark or {},
    }
    write_json(report_dir / "evaluation_report.json", payload)
    write_markdown(report_dir / "evaluation_report.md", "Evaluation Report", payload)
    return payload
