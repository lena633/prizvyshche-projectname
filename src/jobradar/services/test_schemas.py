from typing import Any

import pytest
from pydantic import ValidationError

from jobradar.services.schemas import BudgetIn


@pytest.mark.parametrize(
    ("raw_amount", "should_pass", "expected_amount"),
    [
        ("1500", True, 1500),
        (1500, True, 1500),
        ("  4500  ", True, 4500),
        ("за домовленістю", False, -1),
        (None, False, -1),
    ],
)
def test_amount_is_parsed(
    raw_amount: Any, should_pass: bool, expected_amount: int
) -> None:
    data = {
        "code": "110101",
        "name": "Податок на доходи",
        "amount": raw_amount,
        "location": "expense",
    }

    if not should_pass:
        with pytest.raises(ValidationError):
            BudgetIn(**data)
    else:
        model = BudgetIn(**data)
        assert model.amount == expected_amount


def test_budget_in_to_domain() -> None:
    model = BudgetIn(
        code=" Дніпровська ТГ-7 ",
        name=" Заробітна плата вчителів 7 ",
        amount=1500,
        location="expense",
    )
    domain_obj = model.to_domain()

    assert domain_obj.code == "дніпровська тг-7"
    assert domain_obj.name == "заробітна плата вчителів 7"
    assert domain_obj.amount == 1500
    assert domain_obj.type == "expense"
