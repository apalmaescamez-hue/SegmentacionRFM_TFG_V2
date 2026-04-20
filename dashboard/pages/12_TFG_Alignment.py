from __future__ import annotations

import pandas as pd
import streamlit as st


st.set_page_config(page_title="TFG Alignment", page_icon="🎓", layout="wide")
st.title("🎓 Alineación con el plan de trabajo")
st.caption("Relación explícita entre objetivos académicos, preguntas de investigación y componentes de la app.")

st.subheader("Objetivo general")
st.info(
    """
    Analizar y diseñar una arquitectura reproducible de pipeline de datos para la segmentación RFM,
    evaluando su aplicabilidad como sistema de soporte a la toma de decisiones automatizada en
    estrategias de marketing basadas en datos.
    """
)

st.subheader("Objetivos específicos vs implementación")
objectives = pd.DataFrame(
    [
        {
            "objetivo": "Revisar literatura sobre RFM, pipelines y agentes.",
            "componente_app": "Methodology CRISP-DM, Agents y Reports.",
            "estado": "Cubierto como soporte metodológico; la revisión extensa queda en memoria escrita del TFG.",
        },
        {
            "objetivo": "Identificar fuente de datos pública adecuada.",
            "componente_app": "Overview y EDA.",
            "estado": "Cubierto con Online Retail de UCI.",
        },
        {
            "objetivo": "Evaluar estructura, calidad y limitaciones del dataset.",
            "componente_app": "EDA ampliado y Pipeline.",
            "estado": "Cubierto con nulos, duplicados, cancelaciones, no positivos, temporalidad y outliers.",
        },
        {
            "objetivo": "Diseñar esquema conceptual de base de datos.",
            "componente_app": "Data Model.",
            "estado": "Cubierto conceptualmente mediante entidades, campos y relaciones.",
        },
        {
            "objetivo": "Definir modelo RFM, scoring y clasificación.",
            "componente_app": "Segments, Methodology CRISP-DM y Reports.",
            "estado": "Cubierto con quintiles, thresholds, RFM score y segmentos interpretables.",
        },
        {
            "objetivo": "Diseñar pipeline basado en agentes especializados.",
            "componente_app": "Agents.",
            "estado": "Cubierto con matriz de agentes y funciones deterministas asociadas.",
        },
        {
            "objetivo": "Proponer integración conceptual en grafo orquestador.",
            "componente_app": "Agents.",
            "estado": "Cubierto con grafo conceptual tipo LangGraph.",
        },
        {
            "objetivo": "Evaluar eficiencia, calidad y precisión frente a enfoque manual.",
            "componente_app": "Evaluation y Manual vs Pipeline.",
            "estado": "Cubierto con reproducibilidad, eficiencia, trazabilidad, benchmark y comparación Excel-style.",
        },
        {
            "objetivo": "Analizar aplicabilidad para toma de decisiones de marketing.",
            "componente_app": "Segments, RFM EDA y Manual vs Pipeline.",
            "estado": "Cubierto; se puede ampliar con recomendaciones por segmento.",
        },
        {
            "objetivo": "Analizar implicaciones legales y éticas RGPD.",
            "componente_app": "Ethics RGPD.",
            "estado": "Cubierto conceptualmente.",
        },
        {
            "objetivo": "Identificar limitaciones y líneas futuras.",
            "componente_app": "Ethics RGPD, Methodology CRISP-DM y Reports.",
            "estado": "Cubierto; la discusión final debe desarrollarse en el documento escrito.",
        },
    ]
)
st.dataframe(objectives, use_container_width=True, hide_index=True)

st.subheader("Preguntas de investigación vs evidencia")
questions = pd.DataFrame(
    [
        {
            "pregunta": "¿Qué requisitos técnicos debe cumplir el dataset?",
            "evidencia_app": "EDA, validación y limpieza documentada.",
        },
        {
            "pregunta": "¿Cómo garantizar trazabilidad, coherencia y reproducibilidad?",
            "evidencia_app": "Traceability manifest, checksums, versiones de reglas y outputs Parquet/JSON.",
        },
        {
            "pregunta": "¿Qué rol asumen los agentes especializados?",
            "evidencia_app": "Matriz de Agents, política LLM y grafo conceptual.",
        },
        {
            "pregunta": "¿Cómo coordinar agentes en un grafo?",
            "evidencia_app": "Sankey conceptual y pseudoflujo tipo LangGraph.",
        },
        {
            "pregunta": "¿Mejora frente a enfoque manual?",
            "evidencia_app": "Manual vs Pipeline y métricas de Evaluation.",
        },
        {
            "pregunta": "¿Qué implicaciones RGPD considerar?",
            "evidencia_app": "Ethics RGPD.",
        },
    ]
)
st.dataframe(questions, use_container_width=True, hide_index=True)

st.subheader("Alcance del artefacto")
scope = pd.DataFrame(
    [
        {
            "ámbito": "En alcance",
            "detalle": "Pipeline batch reproducible, RFM determinista, dashboard, evaluación, trazabilidad y explicación de agentes.",
        },
        {
            "ámbito": "Fuera de alcance",
            "detalle": "CRM real, decisiones automatizadas con efectos sobre clientes, inferencia poblacional externa y tratamiento de datos personales reales.",
        },
        {
            "ámbito": "Benchmark",
            "detalle": "KMeans se usa como contraste técnico, no como modelo productivo principal.",
        },
        {
            "ámbito": "Agentes",
            "detalle": "Implementación práctica mediante funciones Python; LLM opcional para insights/reporting; LangGraph como arquitectura conceptual.",
        },
    ]
)
st.dataframe(scope, use_container_width=True, hide_index=True)

st.subheader("Mensaje clave para defensa")
st.success(
    """
    La app materializa el plan de trabajo en un artefacto reproducible y desplegado: no solo calcula
    segmentos RFM, sino que permite auditar el dato, justificar la metodología, comparar contra un
    proceso manual, revisar implicaciones RGPD y explicar cómo los agentes coordinarían el pipeline.
    """
)
