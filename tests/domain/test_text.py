import pytest

from jobradar.domain.text import normalize_name


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("  Заробітна   плата  ", "заробітна плата"),
        ("ПОДАТОК НА ДОХОДИ", "податок на доходи"),
        ("   ", ""),
        ("", ""),
        (None, ""),
    ],
)
def test_normalize_name(raw: str | None, expected: str) -> None:
    assert normalize_name(raw) == expected
