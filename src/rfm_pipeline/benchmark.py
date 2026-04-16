from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .config import RFMConfig
from .io import write_json, write_markdown


def run_kmeans_benchmark(rfm: pd.DataFrame, config: RFMConfig, report_dir: Path | None = None) -> dict:
    report_dir = report_dir or config.paths.reports_dir
    try:
        from sklearn.cluster import KMeans
        from sklearn.metrics import silhouette_score
        from sklearn.preprocessing import RobustScaler
    except Exception as exc:
        report = {"status": "skipped", "reason": f"scikit-learn unavailable: {exc}"}
        write_json(report_dir / "benchmark_kmeans.json", report)
        return report

    features = np.log1p(rfm[["recency", "frequency", "monetary"]].astype(float))
    x_scaled = RobustScaler().fit_transform(features)
    results = {}
    for k in [3, 4, 5, 6]:
        if len(rfm) <= k:
            continue
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = model.fit_predict(x_scaled)
        results[str(k)] = {
            "silhouette": float(silhouette_score(x_scaled, labels)),
            "inertia": float(model.inertia_),
        }
    report = {
        "status": "completed",
        "production_model": "RFM rule-based segments",
        "benchmark_only": True,
        "kmeans_results": results,
    }
    write_json(report_dir / "benchmark_kmeans.json", report)
    write_markdown(report_dir / "benchmark_kmeans.md", "KMeans Benchmark", report)
    return report
