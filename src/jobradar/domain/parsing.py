from .models import Vacancy


def normalize_title(raw: str) -> str:
    return " ".join(raw.split()).lower()


def parse_salary(raw: object) -> int | None:
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def to_vacancy(row: dict) -> Vacancy | None:
    title = row.get("title") or ""
    if not title.strip():
        return None
    return Vacancy(
        title=normalize_title(title),
        company=row.get("company", ""),
        salary=parse_salary(row.get("salary")),
        city=row.get("city", ""),
    )
