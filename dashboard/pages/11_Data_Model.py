from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils import load_json


st.set_page_config(page_title="Data Model", page_icon="🗃️", layout="wide")
st.title("🗃️ Esquema conceptual de datos")
st.caption("Modelo conceptual que conecta dataset raw, datos limpios, features RFM, segmentos y artefactos de auditoría.")

traceability = load_json("reports/traceability_manifest.json")

st.subheader("Entidades principales")
entities = pd.DataFrame(
    [
        {
            "entidad": "RAW_TRANSACTIONS",
            "nivel": "Bronze / raw",
            "descripción": "Copia original del dataset Online Retail sin modificar.",
            "clave": "InvoiceNo + StockCode + CustomerID + InvoiceDate",
            "artefacto": "data/raw/Online_Retail.csv",
        },
        {
            "entidad": "CLEAN_TRANSACTIONS",
            "nivel": "Silver / clean",
            "descripción": "Transacciones depuradas: sin CustomerID nulo, cancelaciones, cantidades/precios no positivos y duplicados.",
            "clave": "InvoiceNo + StockCode + CustomerID",
            "artefacto": "data/processed/online_retail_clean.parquet",
        },
        {
            "entidad": "CUSTOMER_RFM",
            "nivel": "Gold / features",
            "descripción": "Agregación cliente con Recency, Frequency y Monetary.",
            "clave": "customer_id",
            "artefacto": "data/processed/customer_rfm.parquet",
        },
        {
            "entidad": "CUSTOMER_SEGMENTS",
            "nivel": "Gold / decision support",
            "descripción": "Scores RFM, score compuesto y segmento accionable.",
            "clave": "customer_id",
            "artefacto": "data/processed/customer_segments.parquet",
        },
        {
            "entidad": "TRACEABILITY_MANIFEST",
            "nivel": "Audit",
            "descripción": "Run ID, checksum, versión de reglas y hash de artefactos.",
            "clave": "run_id",
            "artefacto": "reports/traceability_manifest.json",
        },
    ]
)
st.dataframe(entities, use_container_width=True, hide_index=True)

st.subheader("Campos conceptuales")
fields = pd.DataFrame(
    [
        {"entidad": "RAW_TRANSACTIONS", "campo": "InvoiceNo", "tipo": "string", "uso": "Identificar factura y cancelaciones."},
        {"entidad": "RAW_TRANSACTIONS", "campo": "StockCode", "tipo": "string", "uso": "Identificar producto."},
        {"entidad": "RAW_TRANSACTIONS", "campo": "Description", "tipo": "string", "uso": "Descripción de producto para EDA."},
        {"entidad": "RAW_TRANSACTIONS", "campo": "Quantity", "tipo": "numeric", "uso": "Unidades compradas y filtros de calidad."},
        {"entidad": "RAW_TRANSACTIONS", "campo": "InvoiceDate", "tipo": "datetime", "uso": "Temporalidad y cálculo de recency."},
        {"entidad": "RAW_TRANSACTIONS", "campo": "UnitPrice", "tipo": "numeric", "uso": "Precio unitario y cálculo monetario."},
        {"entidad": "RAW_TRANSACTIONS", "campo": "CustomerID", "tipo": "string", "uso": "Unidad de análisis cliente."},
        {"entidad": "RAW_TRANSACTIONS", "campo": "Country", "tipo": "string", "uso": "Análisis geográfico."},
        {"entidad": "CUSTOMER_RFM", "campo": "recency", "tipo": "integer", "uso": "Días desde última compra hasta snapshot date."},
        {"entidad": "CUSTOMER_RFM", "campo": "frequency", "tipo": "integer", "uso": "Número de facturas/compras válidas."},
        {"entidad": "CUSTOMER_RFM", "campo": "monetary", "tipo": "float", "uso": "Gasto acumulado: Quantity × UnitPrice."},
        {"entidad": "CUSTOMER_SEGMENTS", "campo": "r_score/f_score/m_score", "tipo": "integer", "uso": "Quintiles RFM."},
        {"entidad": "CUSTOMER_SEGMENTS", "campo": "segment", "tipo": "string", "uso": "Segmento interpretable para marketing."},
    ]
)
st.dataframe(fields, use_container_width=True, hide_index=True)

st.subheader("Relaciones conceptuales")
relations = pd.DataFrame(
    [
        {
            "origen": "RAW_TRANSACTIONS",
            "relación": "se depura en",
            "destino": "CLEAN_TRANSACTIONS",
            "regla": "Validación de columnas, exclusión de cancelaciones, no positivos y registros sin cliente.",
        },
        {
            "origen": "CLEAN_TRANSACTIONS",
            "relación": "se agrega por cliente en",
            "destino": "CUSTOMER_RFM",
            "regla": "Group by CustomerID con last_purchase, nunique InvoiceNo y suma monetaria.",
        },
        {
            "origen": "CUSTOMER_RFM",
            "relación": "se puntúa en",
            "destino": "CUSTOMER_SEGMENTS",
            "regla": "Scoring por quintiles estables y asignación de segmentos por reglas.",
        },
        {
            "origen": "Todos los artefactos",
            "relación": "se auditan mediante",
            "destino": "TRACEABILITY_MANIFEST",
            "regla": "Checksum, versiones de reglas y hash SHA-256 por artefacto.",
        },
    ]
)
st.dataframe(relations, use_container_width=True, hide_index=True)

st.subheader("Diagrama textual")
st.code(
    """
RAW_TRANSACTIONS
    └── cleaning rules ──> CLEAN_TRANSACTIONS
            └── customer aggregation ──> CUSTOMER_RFM
                    └── quintile scoring + rules ──> CUSTOMER_SEGMENTS
                            └── reports + checksums ──> TRACEABILITY_MANIFEST
""",
    language="text",
)

st.subheader("Artefactos auditados")
manifest = traceability.get("artifact_manifest", [])
if manifest:
    st.dataframe(pd.DataFrame(manifest), use_container_width=True)
else:
    st.warning("No se encontró manifiesto de trazabilidad. Ejecuta el pipeline para generarlo.")

st.subheader("Valor para el TFG")
st.markdown(
    """
    Este esquema responde al objetivo académico de diseñar una base estructural coherente para soportar
    el pipeline analítico. Aunque el prototipo usa archivos CSV/Parquet en lugar de una base de datos
    transaccional real, el modelo conceptual queda preparado para migrar a tablas relacionales o a una
    arquitectura tipo data lakehouse.
    """
)
