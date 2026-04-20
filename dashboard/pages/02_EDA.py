from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils import load_clean_transactions, load_json, load_segments, metric_card


st.set_page_config(page_title="EDA", page_icon="🔎", layout="wide")
st.title("🔎 Exploratory Data Analysis")
st.caption(
    "EDA ampliado inspirado en notebooks analíticos: calidad de datos, evolución temporal, "
    "distribuciones, productos, países y lectura RFM."
)

eda = load_json("reports/eda_report.json")
cleaning = load_json("reports/cleaning_report.json")
overview = eda.get("dataset_overview", {})
quality = eda.get("data_quality", {})
business = eda.get("business_summary", {})
clean = load_clean_transactions()
segments = load_segments()

plotly_template = "plotly_white"


def _top_n(series: pd.Series, n: int = 15) -> pd.Series:
    return series.sort_values(ascending=False).head(n)


def _safe_bar(data: pd.DataFrame, x: str, y: str, title: str, color: str | None = None) -> None:
    if data.empty:
        st.info("No hay datos suficientes para este gráfico.")
        return
    fig = px.bar(data, x=x, y=y, color=color, title=title, template=plotly_template)
    fig.update_layout(xaxis_title=x, yaxis_title=y)
    st.plotly_chart(fig, use_container_width=True)


tab_quality, tab_time, tab_business, tab_distributions, tab_rfm = st.tabs(
    [
        "1. Calidad de datos",
        "2. Evolución temporal",
        "3. Países y productos",
        "4. Distribuciones",
        "5. Lectura RFM",
    ]
)

with tab_quality:
    st.subheader("Perfil general del dataset")
    cols = st.columns(5)
    with cols[0]:
        metric_card("Filas raw", overview.get("rows"))
    with cols[1]:
        metric_card("Columnas", overview.get("columns"))
    with cols[2]:
        metric_card("Clientes únicos raw", overview.get("unique_customers"))
    with cols[3]:
        metric_card("Facturas", overview.get("unique_invoices"))
    with cols[4]:
        metric_card("Países", overview.get("unique_countries"))

    st.markdown(f"**Rango temporal:** {overview.get('date_min', '—')} → {overview.get('date_max', '—')}")

    missing = quality.get("missing_by_column", {})
    issue_counts = {
        "duplicados": quality.get("duplicate_rows", 0),
        "facturas canceladas": quality.get("cancelled_invoice_rows", 0),
        "quantity <= 0": quality.get("quantity_non_positive", 0),
        "unit_price <= 0": quality.get("unit_price_non_positive", 0),
        "customer_id missing": missing.get("CustomerID", 0),
    }

    left, right = st.columns(2)
    with left:
        st.subheader("Nulos por columna")
        if missing:
            missing_df = pd.DataFrame(missing.items(), columns=["column", "missing"]).sort_values(
                "missing", ascending=False
            )
            fig = px.bar(missing_df, x="column", y="missing", text="missing", template=plotly_template)
            fig.update_layout(xaxis_title="columna", yaxis_title="nulos")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(missing_df, use_container_width=True)
    with right:
        st.subheader("Principales incidencias raw")
        issue_df = pd.DataFrame(issue_counts.items(), columns=["issue", "rows"]).sort_values(
            "rows", ascending=False
        )
        fig = px.bar(issue_df, x="issue", y="rows", text="rows", template=plotly_template)
        fig.update_layout(xaxis_title="incidencia", yaxis_title="filas")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(issue_df, use_container_width=True)

    st.subheader("Impacto de limpieza")
    initial_rows = cleaning.get("initial_rows")
    clean_rows = cleaning.get("clean_rows")
    if initial_rows and clean_rows:
        removed = initial_rows - clean_rows
        retained_pct = clean_rows / initial_rows * 100
        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card("Filas limpias", clean_rows)
        with c2:
            metric_card("Filas excluidas", removed)
        with c3:
            metric_card("% retenido", f"{retained_pct:.2f}%")
        funnel = go.Figure(
            go.Funnel(
                y=["Raw", "Después de reglas de limpieza"],
                x=[initial_rows, clean_rows],
                textinfo="value+percent initial",
            )
        )
        funnel.update_layout(template=plotly_template)
        st.plotly_chart(funnel, use_container_width=True)

with tab_time:
    st.subheader("Evolución temporal de ventas y actividad")
    if clean.empty:
        st.warning("No se encontró el dataset limpio. Ejecuta primero el pipeline.")
    else:
        work = clean.dropna(subset=["InvoiceDate"]).copy()
        work["month"] = work["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
        work["weekday"] = work["InvoiceDate"].dt.day_name()
        work["hour"] = work["InvoiceDate"].dt.hour

        monthly = (
            work.groupby("month")
            .agg(
                revenue=("line_total", "sum"),
                invoices=("InvoiceNo", "nunique"),
                active_customers=("CustomerID", "nunique"),
                units=("Quantity", "sum"),
            )
            .reset_index()
        )
        fig = px.line(
            monthly,
            x="month",
            y=["revenue", "invoices", "active_customers"],
            markers=True,
            title="Evolución mensual: ingresos, facturas y clientes activos",
            template=plotly_template,
        )
        fig.update_layout(xaxis_title="mes", yaxis_title="valor")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(monthly, use_container_width=True)

        left, right = st.columns(2)
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        with left:
            weekday = (
                work.groupby("weekday", observed=True)
                .agg(revenue=("line_total", "sum"), invoices=("InvoiceNo", "nunique"))
                .reindex(weekday_order)
                .dropna()
                .reset_index()
            )
            _safe_bar(weekday, "weekday", "revenue", "Ingresos por día de la semana")
        with right:
            hourly = work.groupby("hour", as_index=False).agg(
                revenue=("line_total", "sum"), invoices=("InvoiceNo", "nunique")
            )
            fig = px.bar(hourly, x="hour", y="invoices", title="Facturas por hora", template=plotly_template)
            fig.update_layout(xaxis_title="hora", yaxis_title="facturas")
            st.plotly_chart(fig, use_container_width=True)

with tab_business:
    st.subheader("Análisis de países y productos")
    if clean.empty:
        st.warning("No se encontró el dataset limpio. Ejecuta primero el pipeline.")
    else:
        left, right = st.columns(2)
        with left:
            country_revenue = (
                clean.groupby("Country", as_index=False)
                .agg(revenue=("line_total", "sum"), invoices=("InvoiceNo", "nunique"), customers=("CustomerID", "nunique"))
                .sort_values("revenue", ascending=False)
                .head(15)
            )
            _safe_bar(country_revenue, "Country", "revenue", "Top países por ingresos")
        with right:
            top_countries = business.get("top_countries", {})
            if top_countries:
                top_countries_df = pd.DataFrame(top_countries.items(), columns=["country", "rows"])
                _safe_bar(top_countries_df, "country", "rows", "Top países por número de transacciones")

        product_level = (
            clean.groupby(["StockCode", "Description"], dropna=False, as_index=False)
            .agg(revenue=("line_total", "sum"), quantity=("Quantity", "sum"), invoices=("InvoiceNo", "nunique"))
            .sort_values("revenue", ascending=False)
        )

        left, right = st.columns(2)
        with left:
            top_revenue = product_level.head(15).copy()
            top_revenue["product"] = top_revenue["Description"].fillna(top_revenue["StockCode"]).astype(str).str.slice(0, 45)
            fig = px.bar(
                top_revenue,
                x="revenue",
                y="product",
                orientation="h",
                title="Top productos por ingresos",
                template=plotly_template,
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, xaxis_title="ingresos", yaxis_title="producto")
            st.plotly_chart(fig, use_container_width=True)
        with right:
            top_quantity = product_level.sort_values("quantity", ascending=False).head(15).copy()
            top_quantity["product"] = top_quantity["Description"].fillna(top_quantity["StockCode"]).astype(str).str.slice(0, 45)
            fig = px.bar(
                top_quantity,
                x="quantity",
                y="product",
                orientation="h",
                title="Top productos por unidades vendidas",
                template=plotly_template,
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, xaxis_title="unidades", yaxis_title="producto")
            st.plotly_chart(fig, use_container_width=True)

with tab_distributions:
    st.subheader("Distribuciones y outliers")
    if clean.empty:
        st.warning("No se encontró el dataset limpio. Ejecuta primero el pipeline.")
    else:
        sample_size = st.slider("Tamaño de muestra para histogramas", 10_000, min(len(clean), 150_000), 60_000, 10_000)
        sample = clean.sample(n=min(sample_size, len(clean)), random_state=42) if len(clean) > sample_size else clean
        sample = sample.copy()
        sample["line_total_log"] = sample["line_total"].clip(lower=0)

        c1, c2, c3 = st.columns(3)
        with c1:
            fig = px.histogram(sample, x="Quantity", nbins=80, title="Distribución de Quantity", template=plotly_template)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = px.histogram(sample, x="UnitPrice", nbins=80, title="Distribución de UnitPrice", template=plotly_template)
            st.plotly_chart(fig, use_container_width=True)
        with c3:
            fig = px.histogram(
                sample,
                x="line_total_log",
                nbins=80,
                title="Distribución de importe por línea",
                log_y=True,
                template=plotly_template,
            )
            fig.update_layout(xaxis_title="Quantity × UnitPrice", yaxis_title="conteo (log)")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Boxplot de importe por país principal")
        top_country_names = _top_n(clean.groupby("Country")["line_total"].sum(), 8).index.tolist()
        country_sample = sample[sample["Country"].isin(top_country_names)].copy()
        if not country_sample.empty:
            upper = country_sample["line_total"].quantile(0.99)
            fig = px.box(
                country_sample[country_sample["line_total"] <= upper],
                x="Country",
                y="line_total",
                title="Distribución de importe por línea en países top (cap p99)",
                template=plotly_template,
            )
            st.plotly_chart(fig, use_container_width=True)

with tab_rfm:
    st.subheader("Lectura visual de segmentos RFM")
    if segments.empty:
        st.warning("No se encontraron segmentos generados.")
    else:
        dist = segments["segment"].value_counts().reset_index()
        dist.columns = ["segment", "customers"]
        left, right = st.columns(2)
        with left:
            fig = px.pie(
                dist,
                names="segment",
                values="customers",
                hole=0.45,
                title="Distribución de segmentos",
                template=plotly_template,
            )
            st.plotly_chart(fig, use_container_width=True)
        with right:
            fig = px.treemap(
                dist,
                path=["segment"],
                values="customers",
                title="Peso relativo de segmentos",
                template=plotly_template,
            )
            st.plotly_chart(fig, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            fig = px.histogram(segments, x="recency", color="segment", nbins=50, title="Recency por segmento")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = px.histogram(segments, x="frequency", color="segment", nbins=50, title="Frequency por segmento")
            st.plotly_chart(fig, use_container_width=True)
        with c3:
            fig = px.histogram(segments, x="monetary", color="segment", nbins=50, log_y=True, title="Monetary por segmento")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Relación Recency-Monetary")
        fig = px.scatter(
            segments,
            x="recency",
            y="monetary",
            color="segment",
            size="frequency",
            hover_data=["customer_id", "frequency", "rfm_score"],
            title="Clientes por recencia, valor monetario y frecuencia",
            template=plotly_template,
            log_y=True,
        )
        fig.update_layout(xaxis_title="recency: días desde última compra", yaxis_title="monetary (log)")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Perfil medio por segmento")
        segment_profile = (
            segments.groupby("segment", as_index=False)
            .agg(
                customers=("customer_id", "count"),
                recency_mean=("recency", "mean"),
                frequency_mean=("frequency", "mean"),
                monetary_mean=("monetary", "mean"),
                monetary_sum=("monetary", "sum"),
            )
            .sort_values("monetary_sum", ascending=False)
        )
        st.dataframe(segment_profile, use_container_width=True)

        heat = segment_profile.set_index("segment")[["recency_mean", "frequency_mean", "monetary_mean"]]
        normalized = (heat - heat.min()) / (heat.max() - heat.min())
        fig = px.imshow(
            normalized.fillna(0),
            text_auto=".2f",
            aspect="auto",
            title="Mapa de calor normalizado del perfil RFM medio",
            template=plotly_template,
        )
        st.plotly_chart(fig, use_container_width=True)
