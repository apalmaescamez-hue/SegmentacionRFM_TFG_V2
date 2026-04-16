from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd

from .config import RFMConfig
from .io import sha256_file, write_json


REQUIRED_COLUMNS = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
]


def ingest_raw(config: RFMConfig, report_dir: Path | None = None) -> dict:
    source = config.paths.source_csv
    if not source.exists():
        raise FileNotFoundError(f"Source CSV not found: {source}")

    raw_copy = config.paths.raw_dir / source.name
    if not raw_copy.exists():
        shutil.copy2(source, raw_copy)

    df = pd.read_csv(source, encoding_errors="replace")
    dates = pd.to_datetime(df["InvoiceDate"], errors="coerce") if "InvoiceDate" in df else pd.Series([])
    metadata = {
        "source_path": str(source),
        "raw_copy_path": str(raw_copy),
        "dataset_checksum": sha256_file(source),
        "rows": int(len(df)),
        "columns": list(df.columns),
        "required_columns_missing": [col for col in REQUIRED_COLUMNS if col not in df.columns],
        "invoice_date_min": dates.min() if len(dates) else None,
        "invoice_date_max": dates.max() if len(dates) else None,
    }
    write_json((report_dir or config.paths.reports_dir) / "raw_metadata.json", metadata)
    return metadata
