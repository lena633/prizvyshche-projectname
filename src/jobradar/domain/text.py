def normalize_name(raw: str | None) -> str: 
    if not raw or not raw.strip():
        return ""

    return " ".join(raw.split()).lower()
