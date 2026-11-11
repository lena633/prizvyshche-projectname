import logging
from collections.abc import Iterator
from itertools import islice
from pathlib import Path
from typing import Any

import pytest

from jobradar.cli import main
from jobradar.services.pipeline import Pipeline, PipelineStats
from jobradar.services.ports import Sourse
from jobradar.sources.json_file import JsonlSource


def test_parse_all_is_lazy(row: dict[str, Any]) -> None:
    """Крок 3: Проверяет ленивость конвейера."""
    consumed = 0

    def endless() -> Iterator[dict[str, Any]]:
        nonlocal consumed
        while True:
            consumed += 1
            yield row.copy()

    class EndlessSource(Sourse):
        name: str = "endless"

        def read(self) -> Iterator[dict[str, Any]]:
            return endless()

    pipeline = Pipeline([EndlessSource()])
    stats = PipelineStats()
    taken = list(islice(pipeline._parse(EndlessSource(), stats), 3))

    assert len(taken) == 3
    assert consumed == 3


def test_malformed_line_is_skipped_and_logged(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Крок 5: Проверка пропуска битых строк."""
    path = tmp_path / "broken.jsonl"
    path.write_text(
        '{"code": "1101", "name": "A", "amount": 100, "location": "expense"}\n'
        "{not json}\n"
        '{"code": "1102", "name": "B", "amount": 200, "location": "expense"}\n',
        encoding="utf-8",
    )

    caplog.set_level(logging.DEBUG, logger="jobradar.sources.json_file")
    rows = list(JsonlSource(path).read())
    assert len(rows) == 2
    assert "skip malformed line 2" in caplog.text


def test_missing_file_exits_with_code_1(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Крок 5: Проверка падения CLI с кодом 1."""
    monkeypatch.setattr("sys.argv", ["jobradar", str(tmp_path / "no.jsonl")])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1


def test_flag_beats_environment(
    jsonl_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Крок 6: Проверка приоритетов конфигурации (аргумент CLI > env)."""
    levels: list[str] = []
    monkeypatch.setattr("jobradar.cli.setup", levels.append)
    monkeypatch.setenv("LOG_LEVEL", "ERROR")
    monkeypatch.setattr(
        "sys.argv", ["jobradar", str(jsonl_file), "--log-level", "DEBUG"]
    )
    main()
    assert levels == ["DEBUG"]
