# tests/services/test_pipeline.py
from collections.abc import Iterator
from typing import Any

from jobradar.services.pipeline import Pipeline


# 1. Создаем поддельный источник данных (Fake/Mock) специально для тестов
class FakeSource:
    # Подделка полностью имитирует настоящий источник: у неё есть имя и метод read()
    name = "fake_source"

    def __init__(self, raw_data: list[dict[str, Any]]) -> None:
        self._raw_data = raw_data

    def read(self) -> Iterator[dict[str, Any]]:
        # Вместо открытия файла просто лениво отдаем словари из памяти
        yield from self._raw_data


# 2. Тест №1: Проверяем базовый подсчет и фильтрацию дубликатов
def test_pipeline_calculates_correct_stats_and_removes_duplicates() -> None:
    # Готовим тестовые «сырые» данные, имитируя строки из файла
    # (Убедитесь, что поля соответствуют вашей схеме BudgetIn)
    mock_rows = [
        {"code": "київська-1", "name": "Транзакція 1", "amount": "1000"},
        {"code": "київська-1", "name": "Транзакція 1", "amount": "1000"},  # Дубликат!
        {"code": "одеська-2", "name": "Транзакція 2", "amount": "5000"},
        {"code": "харківська-3", "name": "Транзакція 3", "amount": "3000"},
    ]

    # Инициализируем подделку и внедряем её в Pipeline (Dependency Injection)
    fake_source = FakeSource(mock_rows)
    pipeline = Pipeline(sources=[fake_source])

    # Запускаем конвейер
    stats = pipeline.run()

    # Проверяем количественные показатели
    assert stats.read == 4
    assert stats.duplicates == 1
    assert stats.kept == 3

    # Проверяем финансовые показатели (min, max, avg)
    assert stats.amount_min == 1000
    assert stats.amount_max == 5000
    assert stats.amount_sum == 9000
    assert stats.amount_avg == 3000.0

    # Проверяем правильность группировки по громадам (с очисткой дефисов)
    assert stats.by_community["київська"] == 1
    assert stats.by_community["одеська"] == 1
    assert stats.by_community["харківська"] == 1


# 3. Тест №2: Проверяем реакцию конвейера на поврежденные/невалидные данные
def test_pipeline_handles_invalid_data_gracefully() -> None:
    mock_rows = [
        {"code": "київська-1", "name": "Правильна", "amount": "2000"},
        {
            "code": "",
            "name": "Пошкоджена (нет кода)",
            "amount": "2000",
        },  # Вызовет ValidationError
        {"code": "одеська-2", "name": "Не валідна сума", "amount": "not-a-number"},
    ]

    fake_source = FakeSource(mock_rows)
    pipeline = Pipeline(sources=[fake_source])
    stats = pipeline.run()

    # Проверяем, что битые записи отсеиваются в stats.invalid
    assert stats.read == 3
    # Количество невалидных зависит от строгих правил в вашей BudgetIn схеме.
    # Если схема требует обязательный код, то пустая строка запишется в stats.invalid
    assert stats.invalid >= 1
