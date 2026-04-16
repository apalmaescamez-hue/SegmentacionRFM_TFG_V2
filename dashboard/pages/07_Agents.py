from __future__ import annotations

import pandas as pd
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

st.subheader("Política de LLM")
st.markdown(
    """
    - **Sin LLM**: ingesta, validación, limpieza, features RFM, segmentación y benchmark.
    - **LLM opcional**: Insight Generator y Report Builder.
    - **Fuente de verdad**: artefactos JSON/Parquet generados por Python determinista.
    - **Regla**: un LLM no modifica datos críticos ni thresholds directamente.
    """
)
