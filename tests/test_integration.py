import logging
from pathlib import Path

import pytest

# Импортируйте вашу главную функцию CLI, обычно это main из jobradar.cli или __main__
from jobradar.cli import main  # ЗАМЕНИТЕ на ваш реальный импорт CLI-точки входа
from jobradar.sources.json_file import JsonlSource


def test_malformed_line_is_skipped_and_logged(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    path = tmp_path / "broken.jsonl"
    # Записываем битый JSON
    path.write_text(
        '{"code": "1101", "name": "A", "amount": 100}\n{not json}\n{"code": "1102", "name": "B", "amount": 200}\n',
        encoding="utf-8",
    )

    caplog.set_level(logging.DEBUG, logger="jobradar.sources.json_file")

    rows = list(JsonlSource(path).read())
    assert len(rows) == 2
    assert "skip malformed line 2" in caplog.text


def test_missing_file_exits_with_code_1(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Имитируем запуск из консоли с несуществующим файлом
    monkeypatch.setattr("sys.argv", ["jobradar", str(tmp_path / "no.jsonl")])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
