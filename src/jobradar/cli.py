import argparse
from pathlib import Path

from .services.pipeline import count_by_city, load_vacancies


def main() -> None:
    parser = argparse.ArgumentParser(prog="jobradar")
    parser.add_argument("path", type=Path, help="файл із даними")
    args = parser.parse_args()
    vacancies = load_vacancies(args.path)
    print(f"Завантажено записів: {len(vacancies)}")
    for city, count in count_by_city(vacancies).most_common():
        print(f"  {city}: {count}")


if __name__ == "__main__":
    main()
