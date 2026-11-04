import logging
from pathlib import Path

import pytest

from jobradar.config import mask
from jobradar.errors import SourceError
from jobradar.services.pipeline import Pipeline
from jobradar.sources.json_file import JsonlSource  # ИСПРАВЛЕНО имя модуля на jsonl
from tests.services.test_pipeline import ROW, FakeSource


def test_invalid_rows_are_logged_as_warning(caplog) -> None:
    caplog.set_level(logging.DEBUG)
    # ИСПРАВЛЕНО: передаем невалидную структуру с ключом 'code', как требует BudgetIn
    Pipeline([FakeSource([ROW, {"code": "", "name": "B", "amount": "100"}])]).run()
    assert "skipped 1 invalid rows" in caplog.text

def test_missing_file_raises_source_error() -> None:
    with pytest.raises(SourceError, match="cannot open"):
        list(JsonlSource(Path("data/no-such.jsonl")).read())

def test_source_error_keeps_original_cause() -> None:
    try:
        list(JsonlSource(Path("data/no-such.jsonl")).read())
    except SourceError as exc:
        assert isinstance(exc.__cause__, FileNotFoundError)
    else:
        raise AssertionError("SourceError not raised")

def test_secret_is_masked() -> None:
    assert mask("super-secret-token-4417") == "*******************4417"
    assert mask("abc") == "****"
