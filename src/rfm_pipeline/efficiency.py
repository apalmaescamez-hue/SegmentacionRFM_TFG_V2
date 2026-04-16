from __future__ import annotations

import time
from contextlib import contextmanager
from pathlib import Path

from .io import write_json, write_markdown


class EfficiencyTracker:
    def __init__(self) -> None:
        self.stage_runtime_seconds: dict[str, float] = {}
        self._start = time.perf_counter()

    @contextmanager
    def stage(self, name: str):
        started = time.perf_counter()
        yield
        self.stage_runtime_seconds[name] = round(time.perf_counter() - started, 6)

    def report(self, rows_processed: int, report_dir: Path) -> dict:
        total = round(time.perf_counter() - self._start, 6)
        payload = {
            "total_runtime_seconds": total,
            "stage_runtime_seconds": self.stage_runtime_seconds,
            "rows_processed": int(rows_processed),
            "rows_per_second": float(rows_processed / total) if total else None,
        }
        write_json(report_dir / "efficiency_report.json", payload)
        write_markdown(report_dir / "efficiency_report.md", "Efficiency Report", payload)
        return payload
