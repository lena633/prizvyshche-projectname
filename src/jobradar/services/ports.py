from collections.abc import Iterable, Iterator
from typing import Any, Protocol

from jobradar.domain.models import BudgetRow


class Sourse(Protocol):
    name: str

    def read(self) -> Iterator[dict[str, Any]]:
        pass


class BudgetRepository(Protocol):
    """Контракт сховища бюджетних записів."""

    def add_many(self, rows: Iterable[BudgetRow]) -> int:
        """Ідемпотентно записує потік бюджетних записів пачками."""
        ...

    def count(self) -> int:
        """Повертає загальну кількість записів у сховищі."""
        ...

    def by_type(self, row_type: str) -> list[BudgetRow]:
        """Повертає всі бюджетні записи вказаного типу."""
        ...

    def top_types(self, limit: int = 5) -> list[tuple[str, int]]:
        """Повертає топ типів за кількістю записів."""
        ...

    def average_amount(self) -> float | None:
        """Повертає середню суму по всіх записах."""
        ...
