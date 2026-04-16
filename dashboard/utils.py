from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

REPORTS_DIR = ROOT / "reports"
PROCESSED_DIR = ROOT / "data" / "processed"


@st.cache_data(show_spinner=False)
def load_json(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def load_text(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


@st.cache_data(show_spinner=False)
def load_segments() -> pd.DataFrame:
    parquet = PROCESSED_DIR / "customer_segments.parquet"
    csv = PROCESSED_DIR / "customer_segments.csv"
    if parquet.exists():
        return pd.read_parquet(parquet)
    if csv.exists():
        return pd.read_csv(csv)
    return pd.DataFrame()


def metric_card(label: str, value: Any, help_text: str | None = None) -> None:
    st.metric(label, value if value is not None else "—", help=help_text)


def render_json_download(label: str, relative_path: str) -> None:
    path = ROOT / relative_path
    if path.exists():
        st.download_button(label, path.read_bytes(), file_name=path.name, mime="application/json")


def list_report_files() -> list[Path]:
    if not REPORTS_DIR.exists():
        return []
    return sorted([p for p in REPORTS_DIR.rglob("*") if p.is_file() and p.suffix.lower() in {".json", ".md"}])


AGENT_MATRIX = [
    {
        "name": "Data Collector",
        "phase": "Preparación de datos",
        "implementation": "practical",
        "uses_llm": False,
        "inputs": "CSV raw",
        "outputs": "raw_metadata.json",
        "deterministic_functions": "ingestion.ingest_raw",
    },
    {
        "name": "Data Validator",
        "phase": "Preparación de datos",
        "implementation": "practical",
        "uses_llm": False,
        "inputs": "DataFrame raw",
        "outputs": "validation_report.json",
        "deterministic_functions": "validation.validate_online_retail",
    },
    {
        "name": "Data Cleaner",
        "phase": "Preparación de datos",
        "implementation": "practical",
        "uses_llm": False,
        "inputs": "DataFrame raw + config",
        "outputs": "online_retail_clean.parquet",
        "deterministic_functions": "cleaning.clean_transactions",
    },
    {
        "name": "Feature Engineer",
        "phase": "Pipeline RFM",
        "implementation": "practical",
        "uses_llm": False,
        "inputs": "clean transactions",
        "outputs": "customer_rfm.parquet",
        "deterministic_functions": "features.build_rfm_features",
    },
    {
        "name": "RFM Segmentation",
        "phase": "Pipeline RFM",
        "implementation": "practical",
        "uses_llm": False,
        "inputs": "RFM table + config",
        "outputs": "customer_segments.parquet",
        "deterministic_functions": "segmentation.segment_customers",
    },
    {
        "name": "Benchmark Agent",
        "phase": "Pipeline RFM",
        "implementation": "practical",
        "uses_llm": False,
        "inputs": "RFM table",
        "outputs": "benchmark_kmeans.json",
        "deterministic_functions": "benchmark.run_kmeans_benchmark",
    },
    {
        "name": "Insight Generator",
        "phase": "Validación/Insights",
        "implementation": "mixed",
        "uses_llm": True,
        "inputs": "metrics + segment summaries",
        "outputs": "marketing insights",
        "deterministic_functions": "evaluation reports as grounded input",
    },
    {
        "name": "Report Builder",
        "phase": "Documentación",
        "implementation": "mixed",
        "uses_llm": True,
        "inputs": "reports JSON/MD",
        "outputs": "final report sections",
        "deterministic_functions": "report artifacts as source of truth",
    },
]
