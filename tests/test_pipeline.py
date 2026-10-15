from jobradar.domain.models import BudgetRow
from jobradar.services.pipeline import batched


def test_batched_function_logic() -> None:  # Аннотация возвращаемого значения
    # Создаем список валидных объектов вместо range(5) для mypy
    mock_items = [BudgetRow(code=str(i), name="Test", amount=100, type="income") for i in range(5)]
    
    result = list(batched(mock_items, 2))
    assert len(result) == 3
    assert len(result[0]) == 2
