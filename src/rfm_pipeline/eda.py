from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import RFMConfig
from .io import write_json, write_markdown


def generate_eda_report(df: pd.DataFrame, config: RFMConfig, report_dir: Path | None = None) -> dict:
    report_dir = report_dir or config.paths.reports_dir
    invoice_dates = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    quantities = pd.to_numeric(df["Quantity"], errors="coerce")
    unit_prices = pd.to_numeric(df["UnitPrice"], errors="coerce")
    invoice_no = df["InvoiceNo"].astype(str)

    report = {
        "dataset_overview": {
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "column_names": list(df.columns),
            "date_min": invoice_dates.min(),
            "date_max": invoice_dates.max(),
            "unique_customers": int(df["CustomerID"].dropna().nunique()),
            "unique_invoices": int(df["InvoiceNo"].nunique()),
            "unique_products": int(df["StockCode"].nunique()),
            "unique_countries": int(df["Country"].nunique()),
        },
        "data_quality": {
            "missing_by_column": df.isna().sum().astype(int).to_dict(),
            "duplicate_rows": int(df.duplicated().sum()),
            "cancelled_invoice_rows": int(invoice_no.str.startswith("C", na=False).sum()),
            "quantity_non_positive": int((quantities <= 0).sum()),
            "unit_price_non_positive": int((unit_prices <= 0).sum()),
        },
        "business_summary": {
            "top_countries": df["Country"].value_counts().head(10).astype(int).to_dict(),
            "quantity_sum": float(quantities.sum(skipna=True)),
            "gross_sales_sum": float((quantities * unit_prices).sum(skipna=True)),
        },
    }
    write_json(report_dir / "eda_report.json", report)
    write_markdown(report_dir / "eda_report.md", "EDA Report", report)
    return report
