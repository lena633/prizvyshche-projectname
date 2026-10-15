import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any


# Функция для стандартных JSONL файлов
def read_rows(path: Path) -> Iterator[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue

# Функция для файлов с BOM-маркером (utf-8-sig)
def read_rows_jsonl(path: Path) -> Iterator[dict[str, Any]]: # Исправили аннотацию типов
    with path.open(encoding="utf-8-sig") as f:
        for line in f:
            if not line.strip():
                continue
            try: # Добавили защиту от «битых» строк JSON
                yield json.loads(line)
            except json.JSONDecodeError:
                continue
