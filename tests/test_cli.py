import sys
from pathlib import Path

import pytest

from jobradar import cli


def test_cli_runs_successfully_on_jsonl(
    jsonl_file: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "argv", ["jobradar", str(jsonl_file)])
    cli.main()

    out = capsys.readouterr().out
    assert "Прочитано записів: 4" in out
    assert "Відхилено: 1" in out
    assert "Дублікатів: 1" in out
    assert "Залишилось: 2" in out


def test_cli_exits_with_code_1_on_missing_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    missing = tmp_path / "absent.jsonl"
    monkeypatch.setattr(sys, "argv", ["jobradar", str(missing)])

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 1


def test_cli_exits_with_code_1_on_unsupported_extension(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bad_file = tmp_path / "data.txt"
    bad_file.write_text("hello", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["jobradar", str(bad_file)])

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 1


def test_cli_flag_overrides_env_log_level(
    jsonl_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Крок 6: прапорець --log-level має перекривати змінну середовища LOG_LEVEL."""
    captured: list[str] = []
    monkeypatch.setattr(cli, "setup", lambda level: captured.append(level))
    monkeypatch.setenv("LOG_LEVEL", "ERROR")
    monkeypatch.setattr(
        sys, "argv", ["jobradar", "--log-level", "DEBUG", str(jsonl_file)]
    )

    cli.main()
    assert captured == ["DEBUG"]


def test_cli_uses_env_log_level_when_flag_not_passed(
    jsonl_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Крок 6: без прапорця використовується значення з оточення / Settings."""
    captured: list[str] = []
    monkeypatch.setattr(cli, "setup", lambda level: captured.append(level))
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    monkeypatch.setattr(sys, "argv", ["jobradar", str(jsonl_file)])

    cli.main()
    assert captured == ["WARNING"]
