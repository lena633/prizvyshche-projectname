from collections.abc import Iterator
from typing import Any

from jobradar.services.pipeline import Pipeline

# Выносим эталонную строку наружу, чтобы её видел test_logging.py
ROW = {"code": "київська-1", "name": "Транзакція 1", "amount": "1000"}

# 1. Создаем поддельный источник данных (Fake/Mock) специально для тестов
class FakeSource:
    name = "fake_source"

    def __init__(self, raw_data: list[dict[str, Any]]) -> None:
        self._raw_data = raw_data

    def read(self) -> Iterator[dict[str, Any]]:
        yield from self._raw_data

# 2. Тест №1: Проверяем базовый подсчет и фильтрацию дубликатов
def test_pipeline_calculates_correct_stats_and_removes_duplicates() -> None:
    mock_rows = [
        ROW,
        ROW,  # Дубликат!
        {"code": "одеська-2", "name": "Транзакція 2", "amount": "5000"},
        {"code": "харківська-3", "name": "Транзакція 3", "amount": "3000"},
    ]

    fake_source = FakeSource(mock_rows)
    pipeline = Pipeline(sources=[fake_source])
    stats = pipeline.run()

    assert stats.read == 4
    assert stats.duplicates == 1
    assert stats.kept == 3
    assert stats.amount_min == 1000
    assert stats.amount_max == 5000
    assert stats.amount_sum == 9000
    assert stats.amount_avg == 3000.0

# 3. Тест №2: Проверяем реакцию конвейера на поврежденные/невалидные данные
def test_pipeline_handles_invalid_data_gracefully() -> None:
    mock_rows = [
        ROW,
        {"code": "", "name": "Пошкоджена (нет кода)", "amount": "2000"},  
        {"code": "одеська-2", "name": "Не валідна сума", "amount": "not-a-number"},
    ]

    fake_source = FakeSource(mock_rows)
    pipeline = Pipeline(sources=[fake_source])
    stats = pipeline.run()

    assert stats.read == 3
    assert stats.invalid >= 1
