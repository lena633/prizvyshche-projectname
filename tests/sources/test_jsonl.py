from pathlib import Path
from typing import Any

import pytest

from jobradar.errors import SourceError
from jobradar.sources.json_file import JsonlSource


def test_jsonl_source_reads_valid_file(
    jsonl_file: Path, rows: list[dict[str, Any]]
) -> None:
    loaded = list(JsonlSource(jsonl_file).read())
    assert loaded == rows


def test_jsonl_source_skips_blank_and_malformed_lines(tmp_path: Path) -> None:
    file_path = tmp_path / "broken.jsonl"
    file_path.write_text(
        '\n{"code": "101", "name": "Освіта", "amount": "500"}\n'
        "not-a-valid-json\n"
        '{"code": "102", "name": "Медицина", "amount": "700"}\n',
        encoding="utf-8",
    )

    loaded = list(JsonlSource(file_path).read())
    assert len(loaded) == 2
    assert loaded[0]["code"] == "101"
    assert loaded[1]["code"] == "102"


def test_jsonl_source_missing_file_raises_source_error(tmp_path: Path) -> None:
    missing = tmp_path / "missing.jsonl"
    with pytest.raises(SourceError, match="cannot open"):
        list(JsonlSource(missing).read())
