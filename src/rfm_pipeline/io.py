from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dataframe_hash(df: pd.DataFrame) -> str:
    stable = df.sort_index(axis=1).sort_values(list(df.columns)).reset_index(drop=True)
    payload = stable.to_csv(index=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def to_jsonable(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(v) for v in value]
    return value


def write_json(path: str | Path, payload: dict[str, Any]) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(to_jsonable(payload), indent=2, ensure_ascii=False), encoding="utf-8")
    return out


def write_markdown(path: str | Path, title: str, sections: dict[str, Any]) -> Path:
    lines = [f"# {title}", ""]
    for key, value in sections.items():
        lines.extend(
            [
                f"## {key}",
                "",
                "```json",
                json.dumps(to_jsonable(value), indent=2, ensure_ascii=False),
                "```",
                "",
            ]
        )
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def write_dataframe(df: pd.DataFrame, path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        df.to_parquet(out, index=False)
        return out
    except Exception:
        fallback = out.with_suffix(".csv")
        df.to_csv(fallback, index=False)
        return fallback


def read_dataframe(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    if p.suffix.lower() == ".parquet":
        return pd.read_parquet(p)
    return pd.read_csv(p)
