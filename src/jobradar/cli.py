import argparse
import sys
import time
import tracemalloc
from itertools import islice
from pathlib import Path

from .services.pipeline import (
    PipelineStats,
    deduplicate,
    parse_all,
    read_rows_jsonl,
    read_rows_normal_json,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Аналізатор бюджету громад")
    parser.add_argument("path", type=Path, help="Шлях до файлу з бюджетними даними")
    parser.add_argument("--stats", action="store_true", help="Показати повну фінансову статистику")
    parser.add_argument(
        "--preview", type=int, help="Показати прев'ю N бюджетних рядків (ледаче читання)"
    )

    args = parser.parse_args()

    if not args.path.exists():
        print(f"Помилка: Файл не знайдено за шляхом {args.path}")
        sys.exit(1)

    # Ленивый поток чтения
    rows_stream = (
        read_rows_jsonl(args.path)
        if args.path.suffix == ".jsonl"
        else read_rows_normal_json(args.path)
    )

    stats = PipelineStats()

    if args.preview is not None:
        pipeline = deduplicate(parse_all(rows_stream, stats), stats)

        for item in islice(pipeline, args.preview):
            print(item)

        print("...")
        print(f"прочитано рядків: {stats.read} із 200000")
        return

    # === 2. ПОВНА ФІНАНСОВА СТАТИСТИКА ЧЕРЕЗ STATS (КРОК 5) ===
    if args.stats:
        tracemalloc.start()
        t0 = time.perf_counter()

        pipeline = deduplicate(parse_all(rows_stream, stats), stats)

        for budget in pipeline:
            stats.kept += 1

            if "-" in budget.code:
                community_name = budget.code.split("-")[0]
            else:
                community_name = budget.code

            stats.by_community[community_name] += 1

            # Считаем финансовые показатели
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

        elapsed = time.perf_counter() - t0
        peak = tracemalloc.get_traced_memory()[1] / 1024 / 1024
        tracemalloc.stop()

        print(f"Прочитано записів: {stats.read}")
        print(f"Відхилено (без коду): {stats.invalid}")
        print(f"Дублікатів транзакцій: {stats.duplicates}")
        print(f"Залишилось для аналізу: {stats.kept}")

        avg_amount = int(stats.amount_avg) if stats.amount_avg else 0
        print(
            f"Сума видатків: min={stats.amount_min or 0} max={stats.amount_max or 0} avg={avg_amount}"
        )

        print("Розподіл транзакцій за громадами:")
        for community, count in stats.by_community.most_common(5):
            print(f"  {community}: {count}")

        print(f"Час: {elapsed:.2f} с, пік памʼяті: {peak:.1f} МБ")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
