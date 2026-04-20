from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils import AGENT_MATRIX

st.set_page_config(page_title="Agents", page_icon="🤖", layout="wide")
st.title("🤖 Agents")
st.caption("Los agentes coordinan, validan, explican y reportan. No sustituyen la lógica RFM determinista.")

df = pd.DataFrame(AGENT_MATRIX)
st.dataframe(df, use_container_width=True)

st.subheader("Grafo conceptual de agentes")
st.markdown(
    """
    Este grafo representa la **orquestación conceptual tipo LangGraph** descrita en el plan de trabajo.
    En la versión práctica del dashboard, cada nodo se materializa como una función Python determinista
    o como una etapa de reporting. El LLM queda limitado a explicación y generación de texto, nunca al
    cálculo de segmentos.
    """
)

labels = [
    "Data Collector",
    "Data Validator",
    "Data Cleaner",
    "Feature Engineer",
    "RFM Segmentation",
    "Benchmark Agent",
    "Evaluation Agent",
    "Insight Generator",
    "Report Builder",
]
index = {label: i for i, label in enumerate(labels)}
edges = [
    ("Data Collector", "Data Validator"),
    ("Data Validator", "Data Cleaner"),
    ("Data Cleaner", "Feature Engineer"),
    ("Feature Engineer", "RFM Segmentation"),
    ("RFM Segmentation", "Benchmark Agent"),
    ("RFM Segmentation", "Evaluation Agent"),
    ("Benchmark Agent", "Evaluation Agent"),
    ("Evaluation Agent", "Insight Generator"),
    ("Insight Generator", "Report Builder"),
]
fig = go.Figure(
    data=[
        go.Sankey(
            node={
                "pad": 18,
                "thickness": 18,
                "line": {"color": "rgba(0,0,0,0.25)", "width": 0.5},
                "label": labels,
            },
            link={
                "source": [index[src] for src, _ in edges],
                "target": [index[dst] for _, dst in edges],
                "value": [1] * len(edges),
            },
        )
    ]
)
fig.update_layout(title_text="Flujo conceptual multiagente", font_size=12)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Pseudoflujo LangGraph")
st.code(
    """
State = {
    "raw_data": DataFrame,
    "clean_data": DataFrame,
    "rfm_features": DataFrame,
    "segments": DataFrame,
    "metrics": dict,
    "reports": dict
}

DataCollector -> DataValidator -> DataCleaner -> FeatureEngineer
FeatureEngineer -> RFMSegmentation
RFMSegmentation -> BenchmarkAgent
RFMSegmentation -> EvaluationAgent
BenchmarkAgent -> EvaluationAgent
EvaluationAgent -> InsightGenerator -> ReportBuilder
""",
    language="text",
)

st.subheader("Política de LLM")
st.markdown(
    """
    - **Sin LLM**: ingesta, validación, limpieza, features RFM, segmentación y benchmark.
    - **LLM opcional**: Insight Generator y Report Builder.
    - **Fuente de verdad**: artefactos JSON/Parquet generados por Python determinista.
    - **Regla**: un LLM no modifica datos críticos ni thresholds directamente.
    """
)
