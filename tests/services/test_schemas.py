from typing import Any

import pytest
from pydantic import ValidationError

from jobradar.services.schemas import BudgetIn


def test_valid_budget_in_normalizes_and_converts(row: dict[str, Any]) -> None:
    raw = {**row, "code": "  ДНІПРОВСЬКА ТГ-7  ", "name": "  Заробітна   Плата  "}
    item = BudgetIn.model_validate(raw).to_domain()

    assert item.code == "дніпровська тг-7"
    assert item.name == "заробітна плата"
    assert item.amount == 1500
    assert item.type == "expense"


def test_budget_in_accepts_location_alias() -> None:
    item = BudgetIn.model_validate(
        {"code": "101", "name": "Освіта", "amount": "500", "location": "income"}
    ).to_domain()
    assert item.type == "income"


@pytest.mark.parametrize(
    "bad_row",
    [
        {"code": "", "name": "Освіта", "amount": "500"},
        {"code": "101", "name": "   ", "amount": "500"},
        {"code": "101", "name": "Освіта", "amount": "0"},
        {"code": "101", "name": "Освіта", "amount": "-100"},
        {"code": "101", "name": "Освіта", "amount": "за домовленістю"},
    ],
)
def test_budget_in_rejects_invalid_data(bad_row: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        BudgetIn.model_validate(bad_row)
