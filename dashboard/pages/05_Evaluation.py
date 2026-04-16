from __future__ import annotations

import streamlit as st

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils import load_json, metric_card

st.set_page_config(page_title="Evaluation", page_icon="📈", layout="wide")
st.title("📈 Evaluation")

evaluation = load_json("reports/evaluation_report.json")
repro = load_json("reports/reproducibility_report.json") or evaluation.get("reproducibility", {})
efficiency = evaluation.get("efficiency", {})
traceability = evaluation.get("traceability", {})

st.subheader("Reproducibilidad")
cols = st.columns(3)
with cols[0]:
    metric_card("Hash match rate", repro.get("output_hash_match_rate"))
with cols[1]:
    metric_card("Segment stability", repro.get("segment_stability"))
with cols[2]:
    metric_card("RFM numeric delta max", repro.get("rfm_numeric_delta_max"))

st.subheader("Eficiencia")
cols = st.columns(3)
with cols[0]:
    metric_card("Runtime total (s)", efficiency.get("total_runtime_seconds"))
with cols[1]:
    metric_card("Filas procesadas", efficiency.get("rows_processed"))
with cols[2]:
    metric_card("Filas/segundo", round(efficiency.get("rows_per_second", 0), 2) if efficiency.get("rows_per_second") else None)

st.subheader("Trazabilidad")
st.json(
    {
        "run_id": traceability.get("run_id"),
        "dataset_checksum": traceability.get("dataset_checksum"),
        "rules_version": traceability.get("rules_version"),
        "thresholds_version": traceability.get("thresholds_version"),
        "artifact_count": len(traceability.get("artifact_manifest", [])),
    }
)

with st.expander("Evaluation report completo"):
    st.json(evaluation)
