from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import RFMConfig
from .io import write_dataframe, write_json


def resolve_snapshot_date(df: pd.DataFrame, config: RFMConfig) -> pd.Timestamp:
    if config.pipeline.snapshot_date:
        return pd.Timestamp(config.pipeline.snapshot_date)
    return pd.to_datetime(df["InvoiceDate"], errors="coerce").max() + pd.Timedelta(days=1)


def build_rfm_features(
    cleaned: pd.DataFrame, config: RFMConfig, processed_dir: Path | None = None, report_dir: Path | None = None
) -> tuple[pd.DataFrame, dict]:
    processed_dir = processed_dir or config.paths.processed_dir
    report_dir = report_dir or config.paths.reports_dir
    df = cleaned.copy()
    df["total_price"] = df["Quantity"] * df["UnitPrice"]
    snapshot = resolve_snapshot_date(df, config)
    grouped = df.groupby("CustomerID", as_index=False).agg(
        last_purchase=("InvoiceDate", "max"),
        frequency=("InvoiceNo", "nunique"),
        monetary=("total_price", "sum"),
    )
    grouped["recency"] = (snapshot - grouped["last_purchase"]).dt.days.astype(int)
    rfm = grouped[["CustomerID", "recency", "frequency", "monetary"]].rename(
        columns={"CustomerID": "customer_id"}
    )
    output_path = write_dataframe(rfm, processed_dir / "customer_rfm.parquet")
    metadata = {
        "snapshot_date": snapshot,
        "customers": int(len(rfm)),
        "rfm_path": str(output_path),
        "recency_min": int(rfm["recency"].min()),
        "recency_max": int(rfm["recency"].max()),
        "frequency_max": int(rfm["frequency"].max()),
        "monetary_sum": float(rfm["monetary"].sum()),
    }
    write_json(report_dir / "rfm_metadata.json", metadata)
    return rfm, metadata
