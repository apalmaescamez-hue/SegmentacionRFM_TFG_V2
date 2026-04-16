from __future__ import annotations

import streamlit as st

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils import load_json, load_segments, metric_card

st.set_page_config(page_title="Overview", page_icon="🏠", layout="wide")
st.title("🏠 Overview")

eda = load_json("reports/eda_report.json")
segments_report = load_json("reports/rfm_segments.json")
evaluation = load_json("reports/evaluation_report.json")
traceability = load_json("reports/traceability_manifest.json")
segments = load_segments()

overview = eda.get("dataset_overview", {})
efficiency = evaluation.get("efficiency", {})

cols = st.columns(5)
with cols[0]:
    metric_card("Filas raw", overview.get("rows"))
with cols[1]:
    metric_card("Clientes únicos", overview.get("unique_customers"))
with cols[2]:
    metric_card("Facturas", overview.get("unique_invoices"))
with cols[3]:
    metric_card("Clientes segmentados", segments_report.get("customers") or len(segments))
with cols[4]:
    metric_card("Runtime (s)", efficiency.get("total_runtime_seconds"))

st.subheader("Versionado y trazabilidad")
st.json(
    {
        "run_id": traceability.get("run_id"),
        "rules_version": traceability.get("rules_version"),
        "thresholds_version": traceability.get("thresholds_version"),
        "dataset_checksum": traceability.get("dataset_checksum"),
    }
)

st.subheader("Segmentos")
dist = segments_report.get("segment_distribution", {})
if dist:
    st.bar_chart(dist)
    st.dataframe(
        [{"segment": key, "customers": value} for key, value in dist.items()],
        use_container_width=True,
    )
else:
    st.warning("No hay segmentos generados todavía.")
