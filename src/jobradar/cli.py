import argparse
from itertools import islice
from pathlib import Path
import sys
import time
import tracemalloc

# Импортируем ленивые компоненты конвейера бюджета
from .services.pipeline import (
    PipelineStats,
    deduplicate,
    parse_all,
    read_rows_jsonl,
    read_rows_normal_json,
)


def main() -> None:
    # Настраиваем описание утилиты под вашу тему бюджета
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

    # === 1. ПЕРЕВІРКА ЛЕДАЧОСТІ ЧЕРЕЗ PREVIEW (КРОК 7) ===
    if args.preview is not None:
        pipeline = deduplicate(parse_all(rows_stream, stats), stats)

        # Выводим реальные объекты BudgetRow вашей программы бюджета
        for item in islice(pipeline, args.preview):
            print(item)

        print("...")
        print(f"прочитано рядків: {stats.read} із 200000")
        return

    # === 2. ПОВНА ФІНАНСОВА СТАТИСТИКА ЧЕРЕЗ STATS (КРОК 5) ===
    if args.stats:
        tracemalloc.start()
        t0 = time.perf_counter()

        # Строим ленивый конвейер
        pipeline = deduplicate(parse_all(rows_stream, stats), stats)

        # Агрегация за один проход — вычисляем реальные суммы бюджета общин
        for budget in pipeline:
            stats.kept += 1

            # Извлекаем чистое название громады из кода (например, "Київська ТГ-12" -> "Київська ТГ")
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
                # Строки "за домовленістю" безопасно пропускаются в расчете сумм
                pass

        elapsed = time.perf_counter() - t0
        peak = tracemalloc.get_traced_memory()[1] / 1024 / 1024
        tracemalloc.stop()

        # Вывод РЕАЛЬНЫХ результатов вашей программы бюджета:
        print(f"Прочитано записів: {stats.read}")
        print(f"Відхилено (без коду): {stats.invalid}")
        print(f"Дублікатів транзакцій: {stats.duplicates}")
        print(f"Залишилось для аналізу: {stats.kept}")

        avg_amount = int(stats.amount_avg) if stats.amount_avg else 0
        print(
            f"Сума видатків: min={stats.amount_min or 0} max={stats.amount_max or 0} avg={avg_amount}"
        )

        # Выводим реальные общины (ТГ) и сколько транзакций по ним обработано
        print("Розподіл транзакцій за громадами:")
        for community, count in stats.by_community.most_common(5):
            print(f"  {community}: {count}")

        print(f"Час: {elapsed:.2f} с, пік памʼяті: {peak:.1f} МБ")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
