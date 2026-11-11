from dataclasses import FrozenInstanceError

import pytest

from jobradar.domain.models import BudgetRow


def make(**overrides: object) -> BudgetRow:
    """Строит валидную доменную модель BudgetRow, заменяя только нужные поля."""
    data: dict[str, object] = {
        "code": "110101",
        "name": "Податок на доходи",
        "amount": 4500,
        "type": "expense",
    }
    data.update(overrides)
    return BudgetRow(**data)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "overrides",
    [
        {"code": ""},
        {"name": ""},
        {"amount": -5},
        {"amount": 0},
    ],
)
def test_invalid_budget_rejected(overrides: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        make(**overrides)


def test_frozen_model_properties_and_hashable() -> None:
    a = make()
    b = make()

    # 1. Проверка неизменяемости (присвоение должно вызывать ошибку)
    with pytest.raises(FrozenInstanceError):
        a.amount = 5000  # type: ignore[misc]

    # 2. Проверка свойства key (уникальный идентификатор записи)
    assert hasattr(a, "key"), "Модель BudgetRow должна иметь свойство 'key'"

    # 3. Слияние одинаковых записей в множестве (дедупликация)
    assert len({a, b}) == 1
