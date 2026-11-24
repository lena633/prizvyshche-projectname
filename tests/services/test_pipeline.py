from collections.abc import Iterator
from itertools import count
from typing import Any

from jobradar.services.pipeline import Pipeline, PipelineStats
from jobradar.services.ports import Sourse
from tests.conftest import FakeSource


def test_pipeline_counts_4_read_1_invalid_1_duplicate_2_kept(
    rows: list[dict[str, Any]],
) -> None:
    stats = Pipeline([FakeSource(rows)]).run()

    assert stats.read == 4
    assert stats.invalid == 1
    assert stats.duplicates == 1
    assert stats.kept == 2
    assert stats.amount_min == 900
    assert stats.amount_max == 1500
    assert stats.amount_avg == 1200.0


def test_pipeline_empty_stats_avg_is_none() -> None:
    stats = Pipeline([FakeSource([])]).run()
    assert stats.kept == 0
    assert stats.amount_avg is None


class InfiniteSource(Sourse):
    name = "infinite"

    def __init__(self) -> None:
        self.produced = 0

    def read(self) -> Iterator[dict[str, Any]]:
        for idx in count(1):
            self.produced = idx
            yield {
                "code": f"ТГ-{idx}",
                "name": "Стаття видатків",
                "amount": "1000",
                "type": "expense",
            }


def test_pipeline_parse_is_lazy() -> None:
    """Перевірка на лінивість: конвеєр читає рівно стільки записів, скільки запросили."""
    source = InfiniteSource()
    stats = PipelineStats()

    stream = Pipeline._parse(source, stats)
    first_two = [next(stream), next(stream)]

    assert len(first_two) == 2
    assert source.produced == 2
    assert stats.read == 2
