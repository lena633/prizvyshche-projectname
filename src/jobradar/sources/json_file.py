import json
from collections.abc import Iterator
from pathlib import Path


def read_rows(path: Path) -> Iterator[dict]:
    with path.open(encoding="utf-8-sig") as f:
        yield from json.load(f)


def read_rows_jsonl(path: Path) -> Iterator[dict]:
    with path.open(encoding="utf-8-sig") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)
