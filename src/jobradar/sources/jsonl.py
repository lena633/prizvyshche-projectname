import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any


# Перетворюємо на класи
class JsonlSource:
    name = "jsonl"

    def __init__(self, path: Path) -> None:
        self.path = path

    def read(self) -> Iterator[dict[str, Any]]:
        with self.path.open(encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
