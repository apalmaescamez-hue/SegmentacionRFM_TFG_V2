from __future__ import annotations

import pandas as pd
import streamlit as st


st.set_page_config(page_title="Limitations Future", page_icon="🔭", layout="wide")
st.title("🔭 Limitaciones y líneas futuras")
st.caption("Cierre crítico del artefacto para reforzar la discusión académica del TFG.")

st.subheader("Limitaciones del proyecto")
limitations = pd.DataFrame(
    [
        {
            "categoría": "Datos",
            "limitación": "El dataset Online Retail pertenece a un único minorista y a un periodo histórico concreto.",
            "impacto": "Los segmentos son útiles para este caso de estudio, pero no generalizan automáticamente a otros negocios.",
            "mitigación": "Declarar el alcance y validar el pipeline con nuevos datasets antes de uso empresarial.",
        },
        {
            "categoría": "Metodología RFM",
            "limitación": "RFM resume el comportamiento en tres dimensiones y no incorpora variables demográficas, producto o canal.",
            "impacto": "Puede simplificar patrones de compra complejos.",
            "mitigación": "Usar RFM como baseline interpretable y extender con variables adicionales en trabajos futuros.",
        },
        {
            "categoría": "Modelo",
            "limitación": "El modelo principal no es predictivo supervisado; segmenta comportamiento histórico.",
            "impacto": "No estima directamente probabilidad de churn, CLV futuro o propensión de compra.",
            "mitigación": "Añadir modelos predictivos como extensión, manteniendo RFM como capa explicable.",
        },
        {
            "categoría": "Agentes",
            "limitación": "La orquestación LangGraph se presenta como diseño conceptual; las etapas críticas son funciones deterministas.",
            "impacto": "No es todavía un sistema multiagente autónomo completo.",
            "mitigación": "Implementar LangGraph ejecutable para coordinar nodos en futuras iteraciones.",
        },
        {
            "categoría": "RGPD",
            "limitación": "El análisis ético-legal es académico, no una auditoría legal formal.",
            "impacto": "En empresa real haría falta revisar base jurídica, retención, accesos y derechos del interesado.",
            "mitigación": "Incluir evaluación legal y de seguridad antes de despliegues con datos reales.",
        },
        {
            "categoría": "Despliegue",
            "limitación": "Streamlit Cloud sirve como demo analítica, no como arquitectura enterprise de alta disponibilidad.",
            "impacto": "No cubre escalado, autenticación granular ni monitorización productiva avanzada.",
            "mitigación": "Migrar a infraestructura con CI/CD, storage gestionado, observabilidad y control de acceso.",
        },
    ]
)
st.dataframe(limitations, use_container_width=True, hide_index=True)

st.subheader("Líneas futuras")
future_work = pd.DataFrame(
    [
        {
            "línea": "Orquestación LangGraph ejecutable",
            "descripción": "Convertir cada etapa del pipeline en un nodo real con estado compartido, reintentos y logging.",
            "prioridad": "Alta",
        },
        {
            "línea": "Modelos predictivos complementarios",
            "descripción": "Añadir churn prediction, customer lifetime value o propensión de compra como extensión al RFM.",
            "prioridad": "Media",
        },
        {
            "línea": "MLOps/DataOps avanzado",
            "descripción": "Incorporar MLflow, DVC, tests de calidad de datos, CI/CD y monitorización de drift.",
            "prioridad": "Media-alta",
        },
        {
            "línea": "Activación de marketing",
            "descripción": "Conectar segmentos con campañas simuladas, recomendaciones y medición de uplift.",
            "prioridad": "Media",
        },
        {
            "línea": "Base de datos relacional o lakehouse",
            "descripción": "Migrar artefactos CSV/Parquet a tablas con modelo físico, índices y control de permisos.",
            "prioridad": "Media",
        },
        {
            "línea": "Evaluación con más datasets",
            "descripción": "Validar si las reglas y thresholds mantienen utilidad en otros contextos de e-commerce.",
            "prioridad": "Alta académica",
        },
    ]
)
st.dataframe(future_work, use_container_width=True, hide_index=True)

st.subheader("Conclusión crítica")
st.success(
    """
    El artefacto cumple el objetivo del TFG como pipeline RFM reproducible y sistema de apoyo a la decisión.
    Sus limitaciones no invalidan el resultado; delimitan el alcance académico y abren una evolución natural
    hacia una arquitectura DataOps/MLOps más completa.
    """
)
