from collections import Counter
from collections.abc import Iterable, Iterator
from pathlib import Path

from ..domain.models import BudgetRow
from ..domain.parsing import to_budget_item
from ..sources.json_file import read_rows, read_rows_jsonl


def deduplicate(items: Iterable[BudgetRow]) -> Iterator[BudgetRow]:
    seen: set[tuple[str, str]] = set()
    for item in items:
        if item.key not in seen:
            seen.add(item.key)
            yield item


def count_by_type(items: Iterable[BudgetRow]) -> Counter[str]:
    return Counter(item.type for item in items)


def load_budget_data(path: Path) -> list[BudgetRow]:
    if path.suffix == ".jsonl":
        rows = read_rows_jsonl(path)
    else:
        rows = read_rows(path)

    parsed = (to_budget_item(row) for row in rows)
    valid = (item for item in parsed if item is not None)
    return list(deduplicate(valid))
