from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils import load_json, load_segments, metric_card


st.set_page_config(page_title="Segments", page_icon="👥", layout="wide")
st.title("👥 Segmentación RFM")
st.caption(
    "Análisis visual de segmentos: distribución porcentual, contribución monetaria, perfil RFM "
    "y lectura accionable para marketing."
)

segments_report = load_json("reports/rfm_segments.json")
segments = load_segments()

if segments.empty:
    st.warning("No se encontraron segmentos.")
    st.stop()

required = {"customer_id", "segment", "recency", "frequency", "monetary"}
missing = required - set(segments.columns)
if missing:
    st.error(f"Faltan columnas requeridas para el análisis de segmentos: {sorted(missing)}")
    st.stop()

segments = segments.copy()
segments["monetary"] = pd.to_numeric(segments["monetary"], errors="coerce").fillna(0)
segments["frequency"] = pd.to_numeric(segments["frequency"], errors="coerce").fillna(0)
segments["recency"] = pd.to_numeric(segments["recency"], errors="coerce").fillna(0)

PALETTE = {
    "Champions": "#2E7D32",
    "Loyal Customers": "#1565C0",
    "Potential Loyalists": "#00ACC1",
    "New Customers": "#43A047",
    "Need Attention": "#F9A825",
    "At Risk": "#EF6C00",
    "Cannot Lose Them": "#C62828",
    "Hibernating": "#6D4C41",
    "Others": "#757575",
}
fallback_colors = px.colors.qualitative.Bold
for idx, segment_name in enumerate(sorted(segments["segment"].dropna().unique())):
    PALETTE.setdefault(segment_name, fallback_colors[idx % len(fallback_colors)])


def _pct(value: float) -> str:
    return f"{value:.2f}%"


def _money(value: float) -> str:
    return f"€{value:,.0f}"


def _normalize(series: pd.Series, invert: bool = False) -> pd.Series:
    minimum = series.min()
    maximum = series.max()
    if maximum == minimum:
        normalized = pd.Series(100.0, index=series.index)
    else:
        normalized = (series - minimum) / (maximum - minimum) * 100
    return 100 - normalized if invert else normalized


summary = (
    segments.groupby("segment", as_index=False)
    .agg(
        customers=("customer_id", "count"),
        total_monetary=("monetary", "sum"),
        avg_monetary=("monetary", "mean"),
        median_monetary=("monetary", "median"),
        avg_recency=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        recency_median=("recency", "median"),
        frequency_median=("frequency", "median"),
    )
    .sort_values("total_monetary", ascending=False)
)
total_customers = int(summary["customers"].sum())
total_monetary = float(summary["total_monetary"].sum())
summary["customer_pct"] = summary["customers"] / total_customers * 100
summary["monetary_pct"] = summary["total_monetary"] / total_monetary * 100
summary["monetary_per_customer"] = summary["total_monetary"] / summary["customers"]
summary["recency_index"] = _normalize(summary["avg_recency"], invert=True)
summary["frequency_index"] = _normalize(summary["avg_frequency"])
summary["monetary_index"] = _normalize(summary["avg_monetary"])
summary["segment_color"] = summary["segment"].map(PALETTE)
summary_display = summary.copy()
summary_display["customer_pct"] = summary_display["customer_pct"].map(_pct)
summary_display["monetary_pct"] = summary_display["monetary_pct"].map(_pct)
summary_display["total_monetary"] = summary_display["total_monetary"].map(_money)
summary_display["avg_monetary"] = summary_display["avg_monetary"].map(lambda v: f"€{v:,.2f}")
summary_display["monetary_per_customer"] = summary_display["monetary_per_customer"].map(lambda v: f"€{v:,.2f}")

top_customer_segment = summary.sort_values("customers", ascending=False).iloc[0]
top_monetary_segment = summary.sort_values("total_monetary", ascending=False).iloc[0]

cols = st.columns(4)
with cols[0]:
    metric_card("Clientes segmentados", total_customers)
with cols[1]:
    metric_card("Valor monetario total", _money(total_monetary))
with cols[2]:
    metric_card("Segmento con más clientes", top_customer_segment["segment"])
with cols[3]:
    metric_card("Segmento con más valor", top_monetary_segment["segment"])

tab_distribution, tab_monetary, tab_profile, tab_strategy, tab_table = st.tabs(
    [
        "1. Distribución %",
        "2. Valor monetario",
        "3. Perfil RFM",
        "4. Lectura estratégica",
        "5. Buscador y tabla",
    ]
)

with tab_distribution:
    st.subheader("Distribución de segmentos por porcentaje de clientes")
    left, right = st.columns([1.1, 1])
    with left:
        fig = px.pie(
            summary.sort_values("customers", ascending=False),
            names="segment",
            values="customers",
            color="segment",
            color_discrete_map=PALETTE,
            title="Distribución porcentual de clientes por segmento",
        )
        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Clientes: %{value}<br>Porcentaje: %{percent}<extra></extra>",
            marker={"line": {"color": "white", "width": 2}},
        )
        fig.update_layout(legend_title_text="Segmento")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        bar_df = summary.sort_values("customer_pct", ascending=True)
        fig = px.bar(
            bar_df,
            x="customer_pct",
            y="segment",
            orientation="h",
            color="segment",
            color_discrete_map=PALETTE,
            text=bar_df["customer_pct"].map(lambda v: f"{v:.1f}%"),
            title="Ranking de segmentos por % de clientes",
        )
        fig.update_layout(xaxis_title="% de clientes", yaxis_title="", showlegend=False)
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Resumen porcentual")
    st.dataframe(
        summary_display[
            [
                "segment",
                "customers",
                "customer_pct",
                "total_monetary",
                "monetary_pct",
                "avg_recency",
                "avg_frequency",
                "avg_monetary",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

with tab_monetary:
    st.subheader("Valor monetario de cada segmento y peso sobre el total")
    left, right = st.columns([1.2, 1])
    with left:
        monetary_bar = summary.sort_values("total_monetary", ascending=True)
        fig = px.bar(
            monetary_bar,
            x="total_monetary",
            y="segment",
            orientation="h",
            color="segment",
            color_discrete_map=PALETTE,
            text=monetary_bar.apply(lambda r: f"{_money(r['total_monetary'])} · {r['monetary_pct']:.1f}%", axis=1),
            title="Valor monetario total por segmento",
        )
        fig.update_layout(xaxis_title="valor monetario total", yaxis_title="", showlegend=False)
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.pie(
            summary.sort_values("total_monetary", ascending=False),
            names="segment",
            values="total_monetary",
            color="segment",
            color_discrete_map=PALETTE,
            title="% del valor monetario total por segmento",
        )
        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Valor: €%{value:,.0f}<br>Porcentaje: %{percent}<extra></extra>",
            marker={"line": {"color": "white", "width": 2}},
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Pareto de valor monetario")
    pareto = summary.sort_values("total_monetary", ascending=False).copy()
    pareto["cumulative_monetary_pct"] = pareto["total_monetary"].cumsum() / total_monetary * 100
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=pareto["segment"],
            y=pareto["total_monetary"],
            marker_color=[PALETTE[s] for s in pareto["segment"]],
            name="Valor monetario",
            text=pareto["monetary_pct"].map(lambda v: f"{v:.1f}%"),
            textposition="outside",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=pareto["segment"],
            y=pareto["cumulative_monetary_pct"],
            mode="lines+markers+text",
            line={"color": "#111827", "width": 3},
            marker={"size": 9},
            text=pareto["cumulative_monetary_pct"].map(lambda v: f"{v:.0f}%"),
            textposition="top center",
            name="% acumulado",
        ),
        secondary_y=True,
    )
    fig.update_layout(title="Pareto: concentración del valor monetario", xaxis_title="segmento")
    fig.update_yaxes(title_text="valor monetario", secondary_y=False)
    fig.update_yaxes(title_text="% acumulado", range=[0, 110], secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

with tab_profile:
    st.subheader("Perfil RFM por segmento")
    st.markdown(
        """
        Para comparar Recency, Frequency y Monetary en una misma escala, se construye un índice 0-100:
        en **Recency** se invierte la escala porque menos días desde la última compra es mejor.
        """
    )

    order = summary.sort_values("monetary_pct", ascending=False)["segment"].tolist()
    profile = summary.set_index("segment").loc[order].reset_index()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=profile["segment"],
            y=profile["monetary_pct"],
            marker_color=[PALETTE[s] for s in profile["segment"]],
            name="% valor monetario",
            opacity=0.45,
            text=profile["monetary_pct"].map(lambda v: f"{v:.1f}%"),
            textposition="outside",
        ),
        secondary_y=False,
    )
    line_specs = [
        ("recency_index", "Recency index", "#E53935"),
        ("frequency_index", "Frequency index", "#1E88E5"),
        ("monetary_index", "Monetary index", "#43A047"),
    ]
    for column, label, color in line_specs:
        fig.add_trace(
            go.Scatter(
                x=profile["segment"],
                y=profile[column],
                mode="lines+markers",
                name=label,
                line={"color": color, "width": 4},
                marker={"size": 10},
            ),
            secondary_y=True,
        )
    fig.update_layout(
        title="Barras de contribución monetaria + 3 líneas RFM por segmento",
        xaxis_title="segmento",
        legend_title_text="Métrica",
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="% del valor monetario total", secondary_y=False)
    fig.update_yaxes(title_text="índice RFM normalizado 0-100", range=[0, 110], secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)
    with left:
        long_profile = profile.melt(
            id_vars="segment",
            value_vars=["recency_index", "frequency_index", "monetary_index"],
            var_name="metric",
            value_name="index_0_100",
        )
        metric_names = {
            "recency_index": "Recency index",
            "frequency_index": "Frequency index",
            "monetary_index": "Monetary index",
        }
        long_profile["metric"] = long_profile["metric"].map(metric_names)
        fig = px.bar(
            long_profile,
            x="segment",
            y="index_0_100",
            color="metric",
            barmode="group",
            color_discrete_map={
                "Recency index": "#E53935",
                "Frequency index": "#1E88E5",
                "Monetary index": "#43A047",
            },
            title="Comparativa RFM normalizada por segmento",
        )
        fig.update_layout(xaxis_title="segmento", yaxis_title="índice 0-100")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.line(
            long_profile,
            x="segment",
            y="index_0_100",
            color="metric",
            markers=True,
            color_discrete_map={
                "Recency index": "#E53935",
                "Frequency index": "#1E88E5",
                "Monetary index": "#43A047",
            },
            title="Tres líneas RFM con colores diferenciados",
        )
        fig.update_traces(line={"width": 4}, marker={"size": 9})
        fig.update_layout(xaxis_title="segmento", yaxis_title="índice 0-100", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Mapa estratégico de clientes")
    sample = segments.sample(n=min(len(segments), 3000), random_state=42)
    fig = px.scatter(
        sample,
        x="recency",
        y="frequency",
        size="monetary",
        color="segment",
        color_discrete_map=PALETTE,
        hover_data=["customer_id", "monetary", "rfm_score"] if "rfm_score" in sample.columns else ["customer_id", "monetary"],
        title="Recency vs Frequency con tamaño por valor monetario",
        size_max=35,
    )
    fig.update_layout(
        xaxis_title="Recency: días desde última compra",
        yaxis_title="Frequency: número de compras",
        legend_title_text="Segmento",
    )
    st.plotly_chart(fig, use_container_width=True)

with tab_strategy:
    st.subheader("Lectura accionable de segmentos")
    strategy = {
        "Champions": {
            "diagnóstico": "Clientes recientes, frecuentes y con alto valor.",
            "acción": "Programas VIP, acceso anticipado, bundles premium y referral.",
            "prioridad": "Muy alta",
        },
        "Loyal Customers": {
            "diagnóstico": "Compran con frecuencia y sostienen valor recurrente.",
            "acción": "Loyalty program, cross-selling y campañas de retención.",
            "prioridad": "Alta",
        },
        "Potential Loyalists": {
            "diagnóstico": "Buena recencia y potencial de convertirse en clientes fieles.",
            "acción": "Onboarding, recomendaciones personalizadas y segunda compra incentivada.",
            "prioridad": "Alta",
        },
        "New Customers": {
            "diagnóstico": "Clientes recientes, todavía con bajo histórico.",
            "acción": "Welcome journey, educación de producto y oferta de repetición.",
            "prioridad": "Media-alta",
        },
        "Need Attention": {
            "diagnóstico": "Comportamiento intermedio que puede mejorar o deteriorarse.",
            "acción": "Campañas segmentadas de engagement y test A/B de incentivos.",
            "prioridad": "Media",
        },
        "At Risk": {
            "diagnóstico": "Históricamente activos, pero con baja recencia.",
            "acción": "Win-back, descuentos limitados y mensajes de recuperación.",
            "prioridad": "Alta",
        },
        "Cannot Lose Them": {
            "diagnóstico": "Clientes valiosos con señales de abandono.",
            "acción": "Intervención personalizada, soporte preferente y ofertas exclusivas.",
            "prioridad": "Crítica",
        },
        "Hibernating": {
            "diagnóstico": "Baja recencia, baja frecuencia y bajo valor.",
            "acción": "Reactivación de bajo coste o exclusión de campañas caras.",
            "prioridad": "Baja-media",
        },
        "Others": {
            "diagnóstico": "Clientes que no encajan claramente en reglas prioritarias.",
            "acción": "Monitorizar y refinar reglas si el grupo crece.",
            "prioridad": "Baja",
        },
    }
    strategy_df = pd.DataFrame(
        [
            {
                "segment": row["segment"],
                "customers": int(row["customers"]),
                "% clientes": f"{row['customer_pct']:.2f}%",
                "valor total": _money(row["total_monetary"]),
                "% valor": f"{row['monetary_pct']:.2f}%",
                "diagnóstico": strategy.get(row["segment"], {}).get("diagnóstico", "Segmento no definido."),
                "acción recomendada": strategy.get(row["segment"], {}).get("acción", "Revisar manualmente."),
                "prioridad": strategy.get(row["segment"], {}).get("prioridad", "Media"),
            }
            for _, row in summary.sort_values("monetary_pct", ascending=False).iterrows()
        ]
    )
    st.dataframe(strategy_df, use_container_width=True, hide_index=True)

    st.subheader("Matriz valor vs tamaño")
    fig = px.scatter(
        summary,
        x="customer_pct",
        y="monetary_pct",
        size="avg_monetary",
        color="segment",
        color_discrete_map=PALETTE,
        text="segment",
        title="Peso de clientes vs peso de valor monetario",
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(
        xaxis_title="% de clientes",
        yaxis_title="% del valor monetario",
        legend_title_text="Segmento",
    )
    fig.add_shape(
        type="line",
        x0=summary["customer_pct"].mean(),
        x1=summary["customer_pct"].mean(),
        y0=0,
        y1=max(summary["monetary_pct"]) * 1.1,
        line={"dash": "dash", "color": "#9CA3AF"},
    )
    fig.add_shape(
        type="line",
        x0=0,
        x1=max(summary["customer_pct"]) * 1.1,
        y0=summary["monetary_pct"].mean(),
        y1=summary["monetary_pct"].mean(),
        line={"dash": "dash", "color": "#9CA3AF"},
    )
    st.plotly_chart(fig, use_container_width=True)

with tab_table:
    st.subheader("Buscar cliente")
    customer_id = st.text_input("CustomerID")
    if customer_id:
        result = segments[segments["customer_id"].astype(str) == customer_id.strip()]
        if result.empty:
            st.warning("Cliente no encontrado.")
        else:
            st.dataframe(result, use_container_width=True, hide_index=True)

    st.subheader("Tabla de segmentos")
    selected_segment = st.selectbox(
        "Filtrar por segmento",
        ["Todos"] + sorted(segments["segment"].dropna().unique().tolist()),
    )
    view = segments if selected_segment == "Todos" else segments[segments["segment"] == selected_segment]
    st.dataframe(view.head(1000), use_container_width=True, hide_index=True)
    st.caption(f"Mostrando {min(len(view), 1000)} de {len(view)} filas.")

with st.expander("Reporte original de segmentación"):
    st.json(segments_report)
