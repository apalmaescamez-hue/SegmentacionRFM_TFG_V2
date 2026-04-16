from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import RFMConfig
from .io import write_dataframe, write_json, write_markdown


def stable_quantile_score(series: pd.Series, bins: int, higher_is_better: bool = True) -> pd.Series:
    ranked = series.rank(method="first")
    labels = list(range(1, bins + 1))
    scored = pd.qcut(ranked, q=bins, labels=labels, duplicates="drop").astype(int)
    return (bins + 1) - scored if not higher_is_better else scored


def assign_segment(row: pd.Series, labels: dict[str, str]) -> str:
    r, f, m = int(row["r_score"]), int(row["f_score"]), int(row["m_score"])
    if r >= 4 and f >= 4 and m >= 4:
        return labels["champions"]
    if r <= 2 and f >= 4 and m >= 4:
        return labels["cannot_lose"]
    if f >= 4 and m >= 3:
        return labels["loyal"]
    if r >= 4 and f <= 2:
        return labels["new"]
    if r >= 4 and f in (2, 3):
        return labels["potential"]
    if r <= 2 and f >= 3:
        return labels["at_risk"]
    if r == 3 and f <= 3:
        return labels["need_attention"]
    if r <= 2 and f <= 2:
        return labels["hibernating"]
    return labels["others"]


def segment_customers(
    rfm: pd.DataFrame, config: RFMConfig, processed_dir: Path | None = None, report_dir: Path | None = None
) -> tuple[pd.DataFrame, dict]:
    processed_dir = processed_dir or config.paths.processed_dir
    report_dir = report_dir or config.paths.reports_dir
    bins = config.pipeline.rfm_bins
    out = rfm.copy()
    out["r_score"] = stable_quantile_score(out["recency"], bins=bins, higher_is_better=False)
    out["f_score"] = stable_quantile_score(out["frequency"], bins=bins, higher_is_better=True)
    out["m_score"] = stable_quantile_score(out["monetary"], bins=bins, higher_is_better=True)
    out["rfm_score"] = out[["r_score", "f_score", "m_score"]].astype(str).agg("".join, axis=1)
    out["segment"] = out.apply(assign_segment, axis=1, labels=config.segments)
    out["rules_version"] = config.pipeline.rules_version
    out["thresholds_version"] = config.pipeline.thresholds_version

    thresholds = {
        "rules_version": config.pipeline.rules_version,
        "thresholds_version": config.pipeline.thresholds_version,
        "bins": bins,
        "quantiles": {
            col: out[col].quantile([0.2, 0.4, 0.6, 0.8]).to_dict()
            for col in ["recency", "frequency", "monetary"]
        },
    }
    output_path = write_dataframe(out, processed_dir / "customer_segments.parquet")
    report = {
        "segments_path": str(output_path),
        "customers": int(len(out)),
        "segment_distribution": out["segment"].value_counts().astype(int).to_dict(),
        "thresholds": thresholds,
    }
    write_json(report_dir / "thresholds.json", thresholds)
    write_json(report_dir / "rfm_segments.json", report)
    write_markdown(report_dir / "rfm_segments.md", "RFM Segments", report)
    return out, report
