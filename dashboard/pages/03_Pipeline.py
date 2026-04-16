from __future__ import annotations

import pandas as pd
import streamlit as st

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils import load_json

st.set_page_config(page_title="Pipeline", page_icon="⚙️", layout="wide")
st.title("⚙️ Pipeline")

efficiency = load_json("reports/efficiency_report.json")
traceability = load_json("reports/traceability_manifest.json")
cleaning = load_json("reports/cleaning_report.json")
validation = load_json("reports/validation_report.json")

st.subheader("Estado de validación")
if validation.get("passed"):
    st.success("Validación OK")
else:
    st.error("Validación fallida o no disponible")
st.json(validation)

st.subheader("Tiempos por etapa")
stage_times = efficiency.get("stage_runtime_seconds", {})
if stage_times:
    st.dataframe(pd.DataFrame(stage_times.items(), columns=["stage", "seconds"]), use_container_width=True)
    st.bar_chart(stage_times)

st.subheader("Limpieza")
st.json(cleaning)

st.subheader("Manifiesto de artefactos")
manifest = traceability.get("artifact_manifest", [])
if manifest:
    st.dataframe(pd.DataFrame(manifest), use_container_width=True)
else:
    st.warning("No hay manifiesto de artefactos disponible.")
