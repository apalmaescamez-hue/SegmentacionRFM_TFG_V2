from __future__ import annotations

import streamlit as st

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils import load_json, metric_card

st.set_page_config(page_title="Manual vs Pipeline", page_icon="📋", layout="wide")
st.title("📋 Manual vs Pipeline")

manual = load_json("reports/manual_comparison.json")

cols = st.columns(4)
with cols[0]:
    metric_card("Match rate", manual.get("segment_match_rate"))
with cols[1]:
    metric_card("Pasos manuales", manual.get("manual_steps"))
with cols[2]:
    metric_card("Pasos pipeline", manual.get("pipeline_steps"))
with cols[3]:
    metric_card("Runtime manual simulado (s)", manual.get("manual_runtime_seconds"))

st.subheader("Comparación cualitativa")
st.table(
    [
        {"criterio": "Reproducibilidad", "manual/excel": "Limitada", "pipeline": "Alta, script + config"},
        {"criterio": "Trazabilidad", "manual/excel": "Baja/media", "pipeline": "Alta, manifest + checksums"},
        {"criterio": "Errores humanos", "manual/excel": "Mayor", "pipeline": "Menor"},
        {"criterio": "Repetibilidad", "manual/excel": "Manual", "pipeline": "Automática"},
    ]
)

st.subheader("Reporte completo")
st.json(manual)
