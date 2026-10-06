from typing import Any

from .models import BudgetRow


def normalize_name(raw: str) -> str:
    """Видаляє зайві пробіли всередині рядка та переводить у нижній регістр."""
    if not raw or not raw.strip():
        return ""
    return " ".join(raw.split()).lower()


def to_budget_item(row: dict[str, Any]) -> BudgetRow | None:
    """Конвертація сирого словника в об'єкт моделі Валідації."""
    code = str(row.get("code", "")).strip()
    if not code:
        return None

    name = str(row.get("name", "")).strip()

    try:
        return BudgetRow(
            code=code,
            name=normalize_name(name),
            amount=str(row.get("amount", "")).strip(),
            type=str(row.get("type", "")).strip(),
        )
    except (KeyError, ValueError, TypeError):
        return None
