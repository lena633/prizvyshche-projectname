import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from jobradar.services.ports import Sourse


class FakeSource(Sourse):
    """Подставной источник данных, полностью соответствующий интерфейсу Sourse."""

    def __init__(self, items: list[dict[str, Any]], name: str = "fake_source"):
        self.items = items
        self.name = name

    def read(self) -> Iterator[dict[str, Any]]:
        """Реализация абстрактного метода read."""
        return iter(self.items)


@pytest.fixture
def row() -> dict[str, Any]:
    """Один коректний сирий запис."""
    return {
        "code": "Дніпровська ТГ-7",
        "name": "Заробітна плата вчителів 7",
        "amount": "1500",
        "type": "expense",
    }


@pytest.fixture
def rows(row: dict[str, Any]) -> list[dict[str, Any]]:
    """Рівно 4 записи для конвеєра (1 валідний, 1 дублікат, 1 битий, 1 без фіксованої суми)."""
    return [
        row,
        {
            "code": "Дніпровська ТГ-7",
            "name": "Заробітна плата вчителів 7",
            "amount": "1500",
            "type": "expense",
        },
        {
            "code": "",
            "name": "Якась інша стаття",
            "amount": "900",
            "type": "income",
        },
        {
            "code": "Львівська ТГ-2",
            "name": "Закупівля обладнання",
            "amount": "за домовленістю",
            "type": "expense",
        },
    ]


@pytest.fixture
def jsonl_file(tmp_path: Path, rows: list[dict[str, Any]]) -> Path:
    """Тимчасовий .jsonl – зникає разом із tmp_path."""
    path = tmp_path / "vacancies.jsonl"
    body = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows)
    path.write_text(body + "\n", encoding="utf-8")
    return path
