# src/jobradar/cli.py
import argparse
from collections.abc import Callable
from pathlib import Path

from .services.pipeline import Pipeline
from .services.ports import Sourse

# ИСПРАВЛЕНО: Импортируем из правильного имени файла согласно структуре
from .sources.csv_file import CsvSource
from .sources.jsonl import JsonlSource

FACTORIES: dict[str, Callable[[Path], Sourse]] = {
    ".jsonl": JsonlSource,
    ".csv": CsvSource,
}


def build_source(path: Path) -> Sourse:
    try:
        factory = FACTORIES[path.suffix]
    except KeyError:
        raise SystemExit(f"unsupported file type: {path.suffix}") from None
    return factory(path)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="jobradar", description="Аналізатор бюджету громад"
    )
    parser.add_argument(
        "paths", nargs="+", type=Path, help="Шляхи до файлів з бюджетними даними"
    )
    parser.add_argument(
        "--stats", action="store_true", help="Показати повну фінансову статистику"
    )

    args = parser.parse_args(argv)

    sources = [build_source(p) for p in args.paths]
    stats = Pipeline(sources).run()

    print(f"Прочитано записів: {stats.read}")
    print(f"Відхилено: {stats.invalid}")
    print(f"Дублікатів: {stats.duplicates}")
    print(f"Залишилось: {stats.kept}")

    print("-" * 40)

    avg_amount = int(stats.amount_avg) if stats.amount_avg else 0
    print(
        f"Сума видатків: min={stats.amount_min or 0} max={stats.amount_max or 0} avg={avg_amount}"
    )

    print("Розподіл транзакцій за громадами (Топ-5):")
    for community, count in stats.by_community.most_common(5):
        print(f"  {community}: {count}")


if __name__ == "__main__":
    main()
