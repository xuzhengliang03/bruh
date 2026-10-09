"""Canonical paths for generated files under ``processed_data``."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProcessedLayout:
    root: Path
    datasets: Path
    tables: Path
    statistics: Path
    plots: Path
    reports: Path
    cache: Path

    @classmethod
    def from_root(cls, root: Path, *, create: bool = False) -> "ProcessedLayout":
        root = Path(root)
        layout = cls(
            root=root,
            datasets=root / "datasets",
            tables=root / "tables",
            statistics=root / "statistics",
            plots=root / "plots",
            reports=root / "reports",
            cache=root / "cache",
        )
        if create:
            root.mkdir(parents=True, exist_ok=True)
            for directory in (
                layout.datasets,
                layout.tables,
                layout.statistics,
                layout.plots,
                layout.reports,
                layout.cache,
            ):
                directory.mkdir(parents=True, exist_ok=True)
        return layout

