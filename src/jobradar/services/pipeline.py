import json
from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from itertools import islice
from pathlib import Path

# Относительные импорты внутри одного пакета
from ..domain.models import BudgetRow
from ..domain.parsing import to_budget_item


# === ИСПРАВЛЕННЫЕ ИМПОРТЫ (УБИРАЕМ ПРЕФИКС src) ===


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


def read_rows_jsonl(path: Path) -> Iterator[dict]:
    """Ленивое чтение JSON Lines построчно."""
    with path.open(encoding="utf-8-sig") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def read_rows_normal_json(path: Path) -> Iterator[dict]:
    """Ленивая выдача словарей из обычного JSON-массива (для тестов)."""
    with path.open(encoding="utf-8-sig") as f:
        data = json.load(f)
        if isinstance(data, list):
            yield from data
        elif isinstance(data, dict):
            yield data


def parse_all(rows: Iterable[dict], stats: PipelineStats) -> Iterator[BudgetRow]:
    for row in rows:
        stats.read += 1
        budget = to_budget_item(row)
        if budget is None:
            stats.invalid += 1
            continue
        yield budget


def deduplicate(items: Iterable[BudgetRow], stats: PipelineStats) -> Iterator[BudgetRow]:
    seen: set[tuple[str, str]] = set()
    for budget in items:
        if budget.key in seen:
            stats.duplicates += 1
            continue
        seen.add(budget.key)
        yield budget


def collect(items: Iterable[BudgetRow], stats: PipelineStats) -> None:
    for budget in items:
        stats.kept += 1
        stats.by_community[budget.code] += 1
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


def batched(items: Iterable[BudgetRow], size: int) -> Iterator[tuple[BudgetRow, ...]]:
    iterator = iter(items)
    while batch := tuple(islice(iterator, size)):
        yield batch


def count_by_type(items: Iterable[BudgetRow]) -> Counter[str]:
    """Рахує скільки у нас статей дохідних (income) та видаткових (expense)."""
    return Counter(item.type for item in items)


def load_budget_data(path: Path) -> list[BudgetRow]:
    """Совместимая ленивая функция для интеграционных тестов."""
    stats = PipelineStats()
    if path.suffix == ".jsonl":
        rows = read_rows_jsonl(path)
    else:
        rows = read_rows_normal_json(path)

    parsed_items = parse_all(rows, stats)
    unique_items = deduplicate(parsed_items, stats)
    return list(unique_items)
