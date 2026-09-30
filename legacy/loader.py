# legacy/loader.py
import json


def process(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Старая процедурная очистка дубликатов с O(n^2) и превращением ошибок в 0
    unique_rows = []
    for row in data:
        name = row.get("name", "").strip().lower()
        if not name:
            continue

        amount_raw = row.get("amount")
        try:
            amount = int(amount_raw)
        except (ValueError, TypeError):
            amount = 0  # Старая логика: нечисловая сумма -> 0

        # Проверка дубликатов по имени
        exists = False
        for u in unique_rows:
            if u[0] == name:
                exists = True
                break

        if not exists:
            unique_rows.append((name, row.get("code", ""), amount, row.get("type", "")))

    return unique_rows
