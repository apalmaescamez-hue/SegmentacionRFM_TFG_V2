from __future__ import annotations

import pandas as pd
import streamlit as st

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils import load_json, metric_card

st.set_page_config(page_title="EDA", page_icon="🔎", layout="wide")
st.title("🔎 Exploratory Data Analysis")

eda = load_json("reports/eda_report.json")
overview = eda.get("dataset_overview", {})
quality = eda.get("data_quality", {})
business = eda.get("business_summary", {})

cols = st.columns(4)
with cols[0]:
    metric_card("Filas", overview.get("rows"))
with cols[1]:
    metric_card("Columnas", overview.get("columns"))
with cols[2]:
    metric_card("Países", overview.get("unique_countries"))
with cols[3]:
    metric_card("Productos", overview.get("unique_products"))

st.subheader("Rango temporal")
st.write(f"{overview.get('date_min', '—')} → {overview.get('date_max', '—')}")

st.subheader("Calidad de datos")
qcols = st.columns(4)
with qcols[0]:
    metric_card("Duplicados", quality.get("duplicate_rows"))
with qcols[1]:
    metric_card("Cancelaciones", quality.get("cancelled_invoice_rows"))
with qcols[2]:
    metric_card("Quantity <= 0", quality.get("quantity_non_positive"))
with qcols[3]:
    metric_card("UnitPrice <= 0", quality.get("unit_price_non_positive"))

missing = quality.get("missing_by_column", {})
if missing:
    st.subheader("Nulos por columna")
    st.dataframe(pd.DataFrame(missing.items(), columns=["column", "missing"]), use_container_width=True)
    st.bar_chart(missing)

top_countries = business.get("top_countries", {})
if top_countries:
    st.subheader("Top países")
    st.bar_chart(top_countries)

st.subheader("Resumen bruto")
st.json(business)
