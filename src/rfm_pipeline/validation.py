from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import RFMConfig
from .ingestion import REQUIRED_COLUMNS
from .io import write_json, write_markdown


def _pandera_schema_validate(df: pd.DataFrame) -> tuple[bool, str | None]:
    """Run a lightweight Pandera schema when the optional dependency is installed.

    The project keeps a manual validation fallback so local/Streamlit environments
    without Pandera can still execute reproducibly.
    """
    try:
        import pandera as pa
        from pandera import Column, DataFrameSchema
    except Exception as exc:
        return False, f"pandera_unavailable: {exc}"

    try:
        schema = DataFrameSchema(
            {
                "InvoiceNo": Column(nullable=False),
                "StockCode": Column(nullable=False),
                "Description": Column(nullable=True),
                "Quantity": Column(nullable=False),
                "InvoiceDate": Column(nullable=False),
                "UnitPrice": Column(nullable=False),
                "CustomerID": Column(nullable=True),
                "Country": Column(nullable=False),
            },
            coerce=False,
            strict=False,
        )
        schema.validate(df, lazy=True)
        return True, None
    except Exception as exc:
        return False, f"pandera_validation_failed: {exc}"


def validate_online_retail(df: pd.DataFrame, config: RFMConfig, report_dir: Path | None = None) -> dict:
    report_dir = report_dir or config.paths.reports_dir
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    pandera_passed, pandera_reason = _pandera_schema_validate(df) if not missing else (False, "missing_required_columns")
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
    report = {
        "passed": passed,
        "validation_engine": "pandera" if pandera_passed else "manual_fallback",
        "pandera_available": pandera_passed or not str(pandera_reason).startswith("pandera_unavailable"),
        "pandera_result": {"passed": pandera_passed, "reason": pandera_reason},
        "missing_columns": missing,
        "type_checks": type_checks,
        "rows": int(len(df)),
    }
    write_json(report_dir / "validation_report.json", report)
    write_markdown(report_dir / "validation_report.md", "Validation Report", report)
    if not passed:
        raise ValueError(f"Validation failed: {report}")
    return report
