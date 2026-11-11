def normalize_name(raw: str | None) -> str:
    """Очищает название бюджетной статьи от лишних пробелов, приводит к нижнему регистру

    и безопасно обрабатывает пустые значения или None.
    """
    if not raw or not raw.strip():
        return ""

    return " ".join(raw.split()).lower()
