from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import RFMConfig
from .ingestion import REQUIRED_COLUMNS
from .io import write_json, write_markdown


def validate_online_retail(df: pd.DataFrame, config: RFMConfig, report_dir: Path | None = None) -> dict:
    report_dir = report_dir or config.paths.reports_dir
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    type_checks = {
        "InvoiceDate_parseable_ratio": float(pd.to_datetime(df.get("InvoiceDate"), errors="coerce").notna().mean())
        if "InvoiceDate" in df
        else 0.0,
        "Quantity_numeric_ratio": float(pd.to_numeric(df.get("Quantity"), errors="coerce").notna().mean())
        if "Quantity" in df
        else 0.0,
        "UnitPrice_numeric_ratio": float(pd.to_numeric(df.get("UnitPrice"), errors="coerce").notna().mean())
        if "UnitPrice" in df
        else 0.0,
    }
    passed = not missing and all(value > 0.95 for value in type_checks.values())
    report = {"passed": passed, "missing_columns": missing, "type_checks": type_checks, "rows": int(len(df))}
    write_json(report_dir / "validation_report.json", report)
    write_markdown(report_dir / "validation_report.md", "Validation Report", report)
    if not passed:
        raise ValueError(f"Validation failed: {report}")
    return report
