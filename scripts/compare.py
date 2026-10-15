import json
import sys
import time
import tracemalloc
from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path


# === 1. МОДЕЛИ ДАННЫХ ===
@dataclass(frozen=True, slots=True)
class BudgetRow:
    code: str
    name: str
    amount: str
    type: str

    @property
    def key(self) -> tuple[str, str]:
        return self.code.strip(), self.name.strip().lower()


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
    with path.open(encoding="utf-8-sig") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def to_budget_item(row: dict) -> BudgetRow | None:
    if not row.get("code"):
        return None
    return BudgetRow(
        code=str(row["code"]),
        name=str(row["name"]),
        amount=str(row["amount"]),
        type=str(row["type"]),
    )


def parse_all(rows: Iterable[dict], stats: PipelineStats) -> Iterator[BudgetRow]:
    for row in rows:
        stats.read += 1
        budget = to_budget_item(row)
        if budget is None:
            stats.invalid += 1
            continue
        yield budget


def deduplicate(items: Iterable[BudgetRow], stats: PipelineStats) -> Iterator[BudgetRow]:
    seen = set()
    for budget in items:
        if budget.key in seen:
            stats.duplicates += 1
            continue
        seen.add(budget.key)
        yield budget


def collect(items: Iterable[BudgetRow], stats: PipelineStats) -> None:
    for budget in items:
        stats.kept += 1
        try:
            val = int(budget.amount)
            stats.amount_count += 1
            stats.amount_sum += val
        except ValueError:
            pass


# === 2. МЕТОДЫ ИЗМЕРЕНИЯ ===
path = Path("data/large.jsonl")


def lazy():
    stats = PipelineStats()
    collect(deduplicate(parse_all(read_rows_jsonl(path), stats), stats), stats)
    return stats.kept


def greedy():
    rows = list(read_rows_jsonl(path))
    parsed = [to_budget_item(r) for r in rows]
    valid = [v for v in parsed if v is not None]
    seen, unique = set(), []
    for v in valid:
        if v.key not in seen:
            seen.add(v.key)
            unique.append(v)
    return len(unique)


# === 3. ТОЧКА ВХОДА БЕНЧМАРКА ===
if __name__ == "__main__":
    if not path.exists():
        print(f"Ошибка! Файл не найден по пути: {path}")
        sys.exit()  # Исправлено на sys.exit()

    print("Запуск замера производительности бюджетов...\n")
    for name, fn in (("генераторний конвеєр", lazy), ("проміжні списки", greedy)):
        tracemalloc.start()
        t0 = time.perf_counter()
        n = fn()
        elapsed = time.perf_counter() - t0
        peak = tracemalloc.get_traced_memory()[1] / 1024 / 1024
        tracemalloc.stop()
        print(f"{name:22} {n} записів {elapsed:.2f} с пік {peak:.1f} МБ")
