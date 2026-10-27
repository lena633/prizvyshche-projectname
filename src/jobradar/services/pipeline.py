from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass, field

from pydantic import ValidationError

from ..domain.models import BudgetRow
from .ports import Sourse
from .schemas import BudgetIn


@dataclass(slots=True)
class PipelineStats:
    read: int = 0
    invalid: int = 0
    duplicates: int = 0
    kept: int = 0
    by_community: Counter[str] = field(default_factory=Counter)
    amount_count: int = 0
    amount_sum: int = 0
    amount_min: int | None = None
    amount_max: int | None = None

    @property
    def amount_avg(self) -> float | None:
        if not self.amount_count:
            return None
        return self.amount_sum / self.amount_count


class Pipeline:
    def __init__(self, sources: list[Sourse]) -> None:
        self._sources = sources

    def run(self) -> PipelineStats:
        stats = PipelineStats()
        # ИСПРАВЛЕНО ДЛЯ mypy: Здесь должен быть набор КОРТЕЖЕЙ, так как budget.key — это tuple
        seen: set[tuple[str, str]] = set()

        for source in self._sources:
            for budget in self._parse(source, stats):
                # Проверка дубликатов по кортежу ключа
                if budget.key in seen:
                    stats.duplicates += 1
                    continue

                seen.add(budget.key)
                stats.kept += 1

                # Выделение чистого имени громады из кода
                if "-" in budget.code:
                    # ИСПРАВЛЕНО: берем [0] элемент сплита, чтобы получить строку str, а не список list
                    community_name = budget.code.split("-")[0]
                else:
                    community_name = budget.code
                stats.by_community[community_name] += 1

                # Финансовый блок расчета показателей
                try:
                    val = int(budget.amount)
                    stats.amount_count += 1
                    stats.amount_sum += val

                    if stats.amount_min is None or val < stats.amount_min:
                        stats.amount_min = val
                    if stats.amount_max is None or val > stats.amount_max:
                        stats.amount_max = val
                except ValueError:
                    pass

        return stats

    @staticmethod
    def _parse(source: Sourse, stats: PipelineStats) -> Iterator[BudgetRow]:
        for row in source.read():
            stats.read += 1
            try:
                yield BudgetIn.model_validate(row).to_domain()
            except ValidationError:
                stats.invalid += 1
                continue
