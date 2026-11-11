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
        (
            "за домовленістю",
            False,
            -1,
        ),  # По вашей логике возвращает -1 и падает на gt=0
        (None, False, -1),
    ],
)
def test_amount_is_parsed(
    raw_amount: Any, should_pass: bool, expected_amount: int
) -> None:
    """Проверяет логику парсинга сумм моделью BudgetIn."""
    data = {
        "code": "110101",
        "name": "Податок на доходи",
        "amount": raw_amount,
        "location": "expense",  # alias для поля type
    }

    if not should_pass:
        with pytest.raises(ValidationError):
            BudgetIn(**data)
    else:
        model = BudgetIn(**data)
        assert model.amount == expected_amount


def test_budget_in_to_domain() -> None:
    """Проверяет корректное создание доменной модели BudgetRow."""
    model = BudgetIn(
        code=" Дніпровська ТГ-7 ",
        name=" Заробітна плата вчителів 7 ",
        amount=1500,
        location="expense",
    )
    domain_obj = model.to_domain()

    # Проверяем, что применилась доменная функция очистки
    assert domain_obj.code == "дніпровська тг-7"
    assert domain_obj.name == "заробітна плата вчителів 7"
    assert domain_obj.amount == 1500
    assert domain_obj.type == "expense"
