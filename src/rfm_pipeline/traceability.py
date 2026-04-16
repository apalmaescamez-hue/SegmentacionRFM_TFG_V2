from __future__ import annotations

import uuid
from pathlib import Path

from .config import RFMConfig
from .io import sha256_file, write_json


def build_artifact_manifest(paths: list[str | Path]) -> list[dict]:
    manifest = []
    for path in paths:
        p = Path(path)
        if p.exists() and p.is_file():
            manifest.append({"path": str(p), "sha256": sha256_file(p), "size_bytes": p.stat().st_size})
    return manifest


def write_traceability_manifest(
    config: RFMConfig, artifact_paths: list[str | Path], report_dir: Path, run_id: str | None = None
) -> dict:
    payload = {
        "run_id": run_id or str(uuid.uuid4()),
        "dataset_checksum": sha256_file(config.paths.source_csv) if config.paths.source_csv.exists() else None,
        "config_version": "configs/rfm.yaml",
        "rules_version": config.pipeline.rules_version,
        "thresholds_version": config.pipeline.thresholds_version,
        "artifact_manifest": build_artifact_manifest(artifact_paths),
    }
    write_json(report_dir / "traceability_manifest.json", payload)
    return payload
