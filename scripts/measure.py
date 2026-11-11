# scripts/measure.py
import time
import tracemalloc
from pathlib import Path

from jobradar.sources.json_file import JsonlSource

path = Path("data/large.jsonl")
for lazy in (True, False):
    tracemalloc.start()
    t0 = time.perf_counter()
    rows = list(JsonlSource(Path(path)).read())
    total = sum(1 for _ in rows)
    peak = tracemalloc.get_traced_memory()[1] / 1024 / 1024
    tracemalloc.stop()
    mode = "генератор" if lazy else "список"
    print(
        f"{mode}: {total} записів, {time.perf_counter() - t0:.2f} с, пік {peak:.1f} МБ"
    )
