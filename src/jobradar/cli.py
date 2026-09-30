# src/budgetanalyzer/cli.py
import argparse
from pathlib import Path
from .services.pipeline import count_by_type, load_budget_data


def main() -> None:
    parser = argparse.ArgumentParser(prog="budget-cli")
    parser.add_argument("path", type=Path, help="Файл з бюджетними даними (.json або .jsonl)")
    args = parser.parse_args()

    items = load_budget_data(args.path)
    print(f"Успішно завантажено та очищено записів: {len(items)}")
    print("Статистика за типами бюджетних статей:")
    for b_type, count in count_by_type(items).most_common():
        type_str = "Доходи (income)" if b_type == "income" else "Видатки (expense)"
        print(f"  {type_str}: {count}")


if __name__ == "__main__":
    main()
