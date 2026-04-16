from __future__ import annotations

import streamlit as st

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils import load_json, load_segments

st.set_page_config(page_title="Segments", page_icon="👥", layout="wide")
st.title("👥 RFM Segments")

segments_report = load_json("reports/rfm_segments.json")
segments = load_segments()

dist = segments_report.get("segment_distribution", {})
if dist:
    st.subheader("Distribución de segmentos")
    st.bar_chart(dist)

if segments.empty:
    st.warning("No se encontraron segmentos.")
    st.stop()

st.subheader("Buscar cliente")
customer_id = st.text_input("CustomerID")
if customer_id:
    result = segments[segments["customer_id"].astype(str) == customer_id.strip()]
    if result.empty:
        st.warning("Cliente no encontrado.")
    else:
        st.dataframe(result, use_container_width=True)

st.subheader("Tabla de segmentos")
selected_segment = st.selectbox("Filtrar por segmento", ["Todos"] + sorted(segments["segment"].dropna().unique().tolist()))
view = segments if selected_segment == "Todos" else segments[segments["segment"] == selected_segment]
st.dataframe(view.head(1000), use_container_width=True)
st.caption(f"Mostrando {min(len(view), 1000)} de {len(view)} filas.")
