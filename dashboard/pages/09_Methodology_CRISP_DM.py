from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils import load_json, metric_card


st.set_page_config(page_title="Methodology CRISP-DM", page_icon="🧭", layout="wide")
st.title("🧭 Metodología CRISP-DM")
st.caption("Conexión explícita entre el plan de trabajo, CRISP-DM y la implementación desplegada.")

eda = load_json("reports/eda_report.json")
evaluation = load_json("reports/evaluation_report.json")
repro = load_json("reports/reproducibility_report.json")
segments = load_json("reports/rfm_segments.json")
traceability = load_json("reports/traceability_manifest.json")

overview = eda.get("dataset_overview", {})
efficiency = evaluation.get("efficiency", {})

cols = st.columns(5)
with cols[0]:
    metric_card("Filas raw", overview.get("rows"))
with cols[1]:
    metric_card("Clientes segmentados", segments.get("customers"))
with cols[2]:
    metric_card("Runtime total (s)", efficiency.get("total_runtime_seconds"))
with cols[3]:
    metric_card("Hash match rate", repro.get("output_hash_match_rate"))
with cols[4]:
    metric_card("Artefactos trazados", len(traceability.get("artifact_manifest", [])))

st.subheader("Mapa CRISP-DM aplicado")
crisp = pd.DataFrame(
    [
        {
            "fase_crisp_dm": "1. Business Understanding",
            "objetivo_en_tfg": "Segmentar clientes para apoyar decisiones de marketing basadas en datos.",
            "implementación_app": "Overview, Segments, Manual vs Pipeline y TFG Alignment.",
            "evidencia": "Segmentos accionables y métricas de evaluación.",
        },
        {
            "fase_crisp_dm": "2. Data Understanding",
            "objetivo_en_tfg": "Evaluar estructura, calidad y limitaciones del dataset Online Retail.",
            "implementación_app": "EDA ampliado: nulos, duplicados, cancelaciones, temporalidad, países y productos.",
            "evidencia": "reports/eda_report.json y visualizaciones EDA.",
        },
        {
            "fase_crisp_dm": "3. Data Preparation",
            "objetivo_en_tfg": "Aplicar reglas reproducibles de limpieza y transformación.",
            "implementación_app": "Pipeline: validación, limpieza y dataset procesado.",
            "evidencia": "reports/cleaning_report.json y data/processed/online_retail_clean.parquet.",
        },
        {
            "fase_crisp_dm": "4. Modeling",
            "objetivo_en_tfg": "Calcular RFM, scoring por cuantiles y clasificación en segmentos interpretables.",
            "implementación_app": "Segments y reglas RFM deterministas.",
            "evidencia": "customer_rfm.parquet, customer_segments.parquet y thresholds.json.",
        },
        {
            "fase_crisp_dm": "5. Evaluation",
            "objetivo_en_tfg": "Evaluar reproducibilidad, eficiencia, trazabilidad y comparación manual.",
            "implementación_app": "Evaluation y Manual vs Pipeline.",
            "evidencia": "reproducibility_report.json, efficiency_report.json y manual_comparison.json.",
        },
        {
            "fase_crisp_dm": "6. Deployment",
            "objetivo_en_tfg": "Desplegar un artefacto consultable para análisis y reporting.",
            "implementación_app": "Streamlit Cloud con reports y artefactos versionados.",
            "evidencia": "Dashboard público y repositorio GitHub.",
        },
    ]
)
st.dataframe(crisp, use_container_width=True, hide_index=True)

st.subheader("Decisión metodológica principal")
st.info(
    """
    El modelo productivo es **RFM determinista por quintiles**, no un clustering como fuente de verdad.
    KMeans queda como benchmark comparativo porque aporta contraste metodológico, pero no sustituye al
    scoring RFM debido a criterios de interpretabilidad, auditabilidad y accionabilidad comercial.
    """
)

st.subheader("Criterios de evaluación")
criteria = pd.DataFrame(
    [
        {
            "criterio": "Reproducibilidad",
            "métrica": "Hash match rate, estabilidad de segmentos y delta numérico RFM.",
            "por_qué_importa": "Demuestra que misma entrada y misma configuración producen el mismo output.",
        },
        {
            "criterio": "Eficiencia",
            "métrica": "Runtime total, runtime por etapa y filas procesadas por segundo.",
            "por_qué_importa": "Compara el pipeline automatizado con procesos manuales/secuenciales.",
        },
        {
            "criterio": "Trazabilidad",
            "métrica": "Run ID, checksum del dataset, versión de reglas, thresholds y artefactos.",
            "por_qué_importa": "Permite auditar cómo se generó cada resultado.",
        },
        {
            "criterio": "Calidad analítica",
            "métrica": "Coherencia de segmentos, distribución RFM y benchmark KMeans.",
            "por_qué_importa": "Evalúa si los segmentos son interpretables y útiles para marketing.",
        },
    ]
)
st.dataframe(criteria, use_container_width=True, hide_index=True)

st.subheader("Lectura para defensa")
st.markdown(
    """
    Esta página permite justificar que el dashboard no es solo una visualización, sino el **artefacto
    desplegado de una metodología CRISP-DM completa**: comprensión del negocio, comprensión de datos,
    preparación, modelado, evaluación y despliegue.
    """
)
