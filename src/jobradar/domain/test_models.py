import pytest

from jobradar.domain.models import BudgetRow


@pytest.mark.parametrize(
    "code,name,amount",
    [
        ("", "Податок на доходи", 4500),
        ("110101", "", 4500),
        ("110101", "Податок на доходи", -5),
        ("110101", "Податок на доходи", 0),
    ],
)
def test_invalid_burget_rejected(code: str, name: str, amount: int) -> None:
    with pytest.raises(ValueError):
        # ИСПРАВЛЕНО: убрали кавычки у аргументов функции
        BudgetRow(code, name, amount, "expense")


def test_frozen_model_is_hashable() -> None:
    a = BudgetRow("110101", "Податок на доходи", 4500, "expense")
    b = BudgetRow("110101", "Податок на доходи", 4500, "expense")
    assert len({a, b}) == 1
