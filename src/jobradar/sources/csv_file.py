import csv
from collections.abc import Iterator
from pathlib import Path
from typing import Any


class CsvSource:
    name = "csv"

    def __init__(self, path: Path) -> None:
        self._path = path

    def read(self) -> Iterator[dict[str, Any]]:
        with self._path.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            # ИСПРАВЛЕНО ДЛЯ ruff: Используем лаконичный yield from
            yield from reader
