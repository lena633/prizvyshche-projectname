import pytest

from jobradar.domain.text import normalize_name


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("  Дніпровська ТГ-7  ", "дніпровська тг-7"),
        ("Заробітна   плата   вчителів", "заробітна плата вчителів"),
        ("", ""),
        ("   ", ""),
        (None, ""),
    ],
)
def test_normalize_name(raw: str | None, expected: str) -> None:
    assert normalize_name(raw) == expected
