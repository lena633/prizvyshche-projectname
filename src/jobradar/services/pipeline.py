from collections import Counter
from collections.abc import Iterable, Iterator
from pathlib import Path

from ..domain.models import Vacancy
from ..domain.parsing import to_vacancy
from ..sources.json_file import read_rows


def deduplicate(items: Iterable[Vacancy]) -> Iterator[Vacancy]:
    seen: set[tuple[str, str]] = set()
    for vacancy in items:
        if vacancy.key not in seen:
            seen.add(vacancy.key)
            yield vacancy


def count_by_city(items: Iterable[Vacancy]) -> Counter[str]:
    return Counter(vacancy.city for vacancy in items)


def load_vacancies(path: Path) -> list[Vacancy]:
    rows = read_rows(path)
    parsed = (to_vacancy(row) for row in rows)
    valid = (v for v in parsed if v is not None)
    return list(deduplicate(valid))
