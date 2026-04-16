from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException

from rfm_pipeline.cli import run_pipeline

ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / "reports"
PROCESSED = ROOT / "data" / "processed"

app = FastAPI(title="RFM Online Retail API", version="0.1.0")


def _json(name: str) -> dict:
    path = REPORTS / name
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Report not found: {name}")
    return json.loads(path.read_text(encoding="utf-8"))


def _segments() -> pd.DataFrame:
    parquet = PROCESSED / "customer_segments.parquet"
    csv = PROCESSED / "customer_segments.csv"
    if parquet.exists():
        return pd.read_parquet(parquet)
    if csv.exists():
        return pd.read_csv(csv)
    raise HTTPException(status_code=404, detail="Segments artifact not found")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/metadata/model-version")
def model_version() -> dict:
    return _json("traceability_manifest.json")


@app.get("/eda")
def eda() -> dict:
    return _json("eda_report.json")


@app.get("/evaluation")
def evaluation() -> dict:
    return _json("evaluation_report.json")


@app.get("/manual-comparison")
def manual_comparison() -> dict:
    return _json("manual_comparison.json")


@app.get("/pipeline/status")
def pipeline_status() -> dict:
    return {
        "efficiency": _json("efficiency_report.json"),
        "traceability": _json("traceability_manifest.json"),
    }


@app.get("/segments")
def segments(limit: int = 100) -> list[dict]:
    return _segments().head(limit).to_dict(orient="records")


@app.get("/segments/{customer_id}")
def segment_by_customer(customer_id: str) -> dict:
    df = _segments()
    result = df[df["customer_id"].astype(str) == str(customer_id)]
    if result.empty:
        raise HTTPException(status_code=404, detail="Customer not found")
    return result.iloc[0].to_dict()


@app.get("/reports")
def reports() -> list[str]:
    return sorted(str(p.relative_to(ROOT)) for p in REPORTS.rglob("*") if p.is_file())


@app.post("/pipeline/run")
def run_pipeline_endpoint() -> dict:
    return run_pipeline()
