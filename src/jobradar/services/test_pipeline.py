from collections.abc import Iterator
from itertools import islice
from typing import Any

from jobradar.services.pipeline import Pipeline, PipelineStats
from jobradar.services.ports import Sourse


def test_parse_all_is_lazy(row: dict[str, Any]) -> None:
    """Проверяет ленивость конвейера: метод _parse не должен читать лишние записи."""
    consumed = 0

    def endless() -> Iterator[dict[str, Any]]:
        nonlocal consumed
        while True:
            consumed += 1
            yield row.copy()

    # Создаем заглушку бесконечного источника, реализующую порт Sourse
    class EndlessSource(Sourse):
        name: str = "endless"

        def read(self) -> Iterator[dict[str, Any]]:
            return endless()

    pipeline = Pipeline([EndlessSource()])
    stats = PipelineStats()

    # Вытягиваем ровно 3 записи из ленивого парсера
    taken = list(islice(pipeline._parse(EndlessSource(), stats), 3))

    assert len(taken) == 3
    assert consumed == 3  # Конвейер взял ровно 3 записи и остановился!
