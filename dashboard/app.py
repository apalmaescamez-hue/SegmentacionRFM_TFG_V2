from __future__ import annotations

import streamlit as st

from utils import load_json, load_segments, metric_card

st.set_page_config(page_title="RFM Online Retail Dashboard", page_icon="📊", layout="wide")

st.title("📊 RFM Online Retail Dashboard")
st.caption("Pipeline reproducible de segmentación RFM, EDA, evaluación y comparación manual.")

eda = load_json("reports/eda_report.json")
segments_report = load_json("reports/rfm_segments.json")
evaluation = load_json("reports/evaluation_report.json")
traceability = load_json("reports/traceability_manifest.json")
segments = load_segments()

overview = eda.get("dataset_overview", {})
quality = eda.get("data_quality", {})
efficiency = evaluation.get("efficiency", {})

col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Filas raw", overview.get("rows"))
with col2:
    metric_card("Clientes únicos", overview.get("unique_customers"))
with col3:
    metric_card("Clientes segmentados", segments_report.get("customers") or len(segments))
with col4:
    metric_card("Runtime total (s)", efficiency.get("total_runtime_seconds"))

st.subheader("Estado general")
status_cols = st.columns(3)
with status_cols[0]:
    st.success("Pipeline ejecutado" if segments_report else "Pipeline pendiente")
with status_cols[1]:
    st.info(f"Reglas: {traceability.get('rules_version', '—')}")
with status_cols[2]:
    st.info(f"Run ID: {traceability.get('run_id', '—')}")

st.subheader("Calidad de datos resumida")
q1, q2, q3, q4 = st.columns(4)
with q1:
    metric_card("Duplicados", quality.get("duplicate_rows"))
with q2:
    metric_card("Cancelaciones", quality.get("cancelled_invoice_rows"))
with q3:
    metric_card("Quantity <= 0", quality.get("quantity_non_positive"))
with q4:
    metric_card("UnitPrice <= 0", quality.get("unit_price_non_positive"))

st.subheader("Distribución de segmentos")
dist = segments_report.get("segment_distribution", {})
if dist:
    st.bar_chart(dist)
else:
    st.warning("No se encontró `reports/rfm_segments.json`. Ejecuta primero el pipeline.")

st.subheader("Navegación")
st.markdown(
    """
    Usa las páginas laterales para revisar:
    - **EDA**: perfil y calidad de datos.
    - **Pipeline**: tiempos, artefactos y trazabilidad.
    - **Segments**: búsqueda y tabla de clientes segmentados.
    - **Evaluation**: reproducibilidad, eficiencia y trazabilidad.
    - **Manual vs Pipeline**: comparación con enfoque tipo Excel.
    - **Agents**: rol práctico/conceptual y uso de LLM.
    - **Reports**: visor/descarga de reportes.
    - **Methodology CRISP-DM**: conexión metodológica con el plan de trabajo.
    - **Ethics RGPD**: privacidad, minimización y limitaciones ético-legales.
    - **Data Model**: esquema conceptual de datos y trazabilidad.
    - **TFG Alignment**: relación explícita entre objetivos académicos y app.
    - **Limitations Future**: limitaciones del artefacto y líneas futuras.
    """
)
