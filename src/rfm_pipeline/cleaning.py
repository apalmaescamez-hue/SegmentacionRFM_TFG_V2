from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import RFMConfig
from .io import write_dataframe, write_json, write_markdown


def _normalize_customer_id(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    return numeric.astype("Int64").astype(str).replace("<NA>", pd.NA)


def clean_transactions(
    df: pd.DataFrame, config: RFMConfig, processed_dir: Path | None = None, report_dir: Path | None = None
) -> tuple[pd.DataFrame, dict]:
    processed_dir = processed_dir or config.paths.processed_dir
    report_dir = report_dir or config.paths.reports_dir
    work = df.copy()
    initial_rows = len(work)

    masks = {
        "missing_customer_id": work["CustomerID"].isna(),
        "cancelled_invoice": work["InvoiceNo"].astype(str).str.startswith("C", na=False),
        "quantity_non_positive": pd.to_numeric(work["Quantity"], errors="coerce") <= 0,
        "unit_price_non_positive": pd.to_numeric(work["UnitPrice"], errors="coerce") <= 0,
        "exact_duplicate": work.duplicated(),
    }
    valid = pd.Series(True, index=work.index)
    if config.cleaning.drop_missing_customer_id:
        valid &= ~masks["missing_customer_id"]
    if config.cleaning.exclude_cancelled_invoices:
        valid &= ~masks["cancelled_invoice"]
    if config.cleaning.require_positive_quantity:
        valid &= ~masks["quantity_non_positive"]
    if config.cleaning.require_positive_unit_price:
        valid &= ~masks["unit_price_non_positive"]

    cleaned = work.loc[valid].copy()
    duplicate_removed_after_filters = 0
    if config.cleaning.drop_exact_duplicates:
        before = len(cleaned)
        cleaned = cleaned.drop_duplicates()
        duplicate_removed_after_filters = before - len(cleaned)
    if cleaned.empty:
        raise ValueError("No valid customer-level transactions remain after cleaning.")

    cleaned["CustomerID"] = _normalize_customer_id(cleaned["CustomerID"])
    cleaned["InvoiceDate"] = pd.to_datetime(cleaned["InvoiceDate"], errors="coerce")
    cleaned["Quantity"] = pd.to_numeric(cleaned["Quantity"], errors="coerce")
    cleaned["UnitPrice"] = pd.to_numeric(cleaned["UnitPrice"], errors="coerce")
    report = {
        "initial_rows": int(initial_rows),
        "clean_rows": int(len(cleaned)),
        "excluded_counts_raw": {name: int(mask.sum()) for name, mask in masks.items()},
        "duplicate_removed_after_filters": int(duplicate_removed_after_filters),
    }
    output_path = write_dataframe(cleaned, processed_dir / "online_retail_clean.parquet")
    report["clean_dataset_path"] = str(output_path)
    write_json(report_dir / "cleaning_report.json", report)
    write_markdown(report_dir / "cleaning_report.md", "Cleaning Report", report)
    return cleaned, report
