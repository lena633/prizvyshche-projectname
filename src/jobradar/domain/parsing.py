from .models import BudgetRow


def normalize_name(raw: str) -> str:
    if not raw or not raw.strip():
        return ""
    return " ".join(raw.split()).lower()


def parse_amount(raw: object) -> int | None:
    try:
        if isinstance(raw, str):
            raw = raw.replace(" ", "")
        return int(raw)
    except (TypeError, ValueError):
        return None


def to_budget_item(row: dict) -> BudgetRow | None:
    name = row.get("name") or ""
    if not name.strip():
        return None
    return BudgetRow(
        code=str(row.get("code", "")).strip(),
        name=normalize_name(name),
        amount=parse_amount(row.get("amount")),
        type=row.get("type", ""),
    )
