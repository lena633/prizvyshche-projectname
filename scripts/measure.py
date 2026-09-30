import time
import tracemalloc
from pathlib import Path
from src.jobradar.sources.json_file import read_rows_jsonl


def main():
    path = Path("data/large.jsonl")
    if not path.exists():
        print("Помилка: файл data/large.jsonl не знайдено! Будь ласка, згенеруйте його.")
        return

    for lazy in (True, False):
        tracemalloc.start()
        t0 = time.perf_counter()

        # Запускаем чтение
        rows = read_rows_jsonl(path) if lazy else list(read_rows_jsonl(path))

        # Проходим по элементам, чтобы симулировать обработку
        total = sum(1 for _ in rows)

        peak = tracemalloc.get_traced_memory()[1] / 1024 / 1024
        tracemalloc.stop()

        mode = "генератор (lazy)" if lazy else "список (greedy)"
        print(
            f"{mode}: {total} записів, {time.perf_counter() - t0:.2f} с, пік пам'яті: {peak:.2f} МБ"
        )


if __name__ == "__main__":
    main()
