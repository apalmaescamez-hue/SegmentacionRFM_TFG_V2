from __future__ import annotations

import pandas as pd
import streamlit as st


st.set_page_config(page_title="Ethics RGPD", page_icon="⚖️", layout="wide")
st.title("⚖️ Ética, privacidad y RGPD")
st.caption("Bloque académico para justificar el uso responsable del dataset y del pipeline automatizado.")

st.subheader("Naturaleza del dato")
st.markdown(
    """
    El proyecto utiliza el dataset público **Online Retail** con datos transaccionales de un minorista
    online. El objetivo es académico y analítico: diseñar y evaluar un pipeline reproducible para
    segmentación RFM.

    El dataset no contiene identificadores directos como nombre, correo electrónico, teléfono o dirección.
    Aun así, `CustomerID` se trata como un identificador **seudonimizado** porque permite agrupar el
    comportamiento de compra de un mismo cliente.
    """
)

st.subheader("Principios RGPD aplicados")
principles = pd.DataFrame(
    [
        {
            "principio": "Minimización de datos",
            "aplicación": "Solo se usan variables necesarias para EDA, limpieza y RFM.",
            "evidencia_en_app": "Variables transaccionales: InvoiceNo, StockCode, Quantity, InvoiceDate, UnitPrice, CustomerID y Country.",
        },
        {
            "principio": "Limitación de finalidad",
            "aplicación": "Uso limitado a investigación académica y demostración técnica.",
            "evidencia_en_app": "No hay activación comercial real ni contacto con clientes.",
        },
        {
            "principio": "No reidentificación",
            "aplicación": "No se intenta inferir la identidad real detrás de CustomerID.",
            "evidencia_en_app": "El dashboard trabaja con segmentos y métricas agregadas.",
        },
        {
            "principio": "Trazabilidad",
            "aplicación": "Cada ejecución produce artefactos, checksums y versiones de reglas.",
            "evidencia_en_app": "Página Pipeline y Evaluation.",
        },
        {
            "principio": "Explicabilidad",
            "aplicación": "La asignación de segmento se basa en reglas RFM interpretables.",
            "evidencia_en_app": "Página Segments y perfiles RFM.",
        },
    ]
)
st.dataframe(principles, use_container_width=True, hide_index=True)

st.subheader("Riesgos y mitigaciones")
risks = pd.DataFrame(
    [
        {
            "riesgo": "Reidentificación indirecta",
            "mitigación": "No cruzar con fuentes externas ni publicar datos personales adicionales.",
        },
        {
            "riesgo": "Uso comercial fuera del alcance académico",
            "mitigación": "Mantener el proyecto como demo académica y no como sistema CRM real.",
        },
        {
            "riesgo": "Decisiones automatizadas sin supervisión",
            "mitigación": "Presentar los segmentos como apoyo a decisión, no como decisión automática vinculante.",
        },
        {
            "riesgo": "Sesgos del dataset",
            "mitigación": "Declarar que el dataset pertenece a un minorista concreto y no generaliza a toda población.",
        },
        {
            "riesgo": "Uso de LLM sobre datos transaccionales",
            "mitigación": "Restringir LLM a explicación/reporting y no enviar datos sensibles ni permitir modificación de thresholds.",
        },
    ]
)
st.dataframe(risks, use_container_width=True, hide_index=True)

st.subheader("Posición ética del sistema")
st.success(
    """
    El sistema se plantea como **herramienta de soporte analítico**. No toma decisiones finales sobre
    clientes, no ejecuta campañas reales y no automatiza consecuencias individuales. Su valor está en
    hacer reproducible, auditable y explicable una segmentación RFM.
    """
)

st.subheader("Limitaciones ético-legales")
st.markdown(
    """
    - La evaluación RGPD es conceptual y académica, no una auditoría legal formal.
    - En un entorno empresarial real sería necesario revisar base jurídica, información al interesado,
      contratos de tratamiento, retención de datos y controles de acceso.
    - El dataset es público, pero `CustomerID` debe tratarse con prudencia como identificador seudonimizado.
    - El modelo RFM simplifica comportamiento de cliente y no debe usarse como único criterio de decisión.
    """
)
