import json
from collections.abc import Iterator
from pathlib import Path


def read_rows(path: Path) -> Iterator[dict]:
    with path.open(encoding="utf-8-sig") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def read_rows_jsonl(path: Path) -> Iterator[dict]:
    with path.open(encoding="utf-8-sig") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)
