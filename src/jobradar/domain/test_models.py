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

    with pytest.raises(FrozenInstanceError):
        a.amount = 5000  # type: ignore[misc]

    assert hasattr(a, "key"), "Модель BudgetRow должна иметь свойство 'key'"
    assert len({a, b}) == 1


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (1500, False),
        (2999, False),
        (3000, True),
        (9000, True),
    ],
)
def test_is_large_level_transaction(amount: int, expected: bool) -> None:
    """Крок 4: Тест новой бизнес-логики крупных транзакций."""
    assert make(amount=amount).is_large_level_transaction is expected
