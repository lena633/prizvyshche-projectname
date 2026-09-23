def normalize_title(raw: str) -> str:
    if not raw or not raw.strip():
        return ""
    return " ".join(raw.split()).lower()
