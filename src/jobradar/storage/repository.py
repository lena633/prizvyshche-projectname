"""SQLAlchemy-реалізація репозиторію бюджетних записів."""

from collections.abc import Iterable

from sqlalchemy import func, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from jobradar.domain.models import BudgetRow
from jobradar.errors import StorageError
from jobradar.storage.models import BudgetRecord


def _to_row(item: BudgetRow) -> dict[str, object]:
    """Перетворює доменний об'єкт BudgetRow у словник для вставки в БД."""
    return {
        "code": item.code.strip(),
        "name": item.name.strip(),
        "amount": item.amount,
        "type": item.type,
    }


def _to_domain(record: BudgetRecord) -> BudgetRow:
    """Перетворює ORM-запис BudgetRecord у доменний об'єкт BudgetRow."""
    return BudgetRow(
        code=record.code,
        name=record.name,
        amount=record.amount,
        type=record.type,
    )


class SqlBudgetRepository:
    """Репозиторій для роботи з таблицею budgets через SQLAlchemy Session."""

    def __init__(self, session: Session, batch_size: int = 500) -> None:
        self._session = session
        self._batch_size = batch_size

    def add_many(self, rows: Iterable[BudgetRow]) -> int:
        """Записує пачками; повторний запуск не створює дублікатів."""
        written = 0
        batch: list[dict[str, object]] = []
        for item in rows:
            batch.append(_to_row(item))
            if len(batch) >= self._batch_size:
                written += self._flush(batch)
                batch = []
        if batch:
            written += self._flush(batch)
        return written

    def _flush(self, batch: list[dict[str, object]]) -> int:
        """Виконує пакетну ідемпотентну вставку в SQLite."""
        try:
            stmt = (
                insert(BudgetRecord)
                .values(batch)
                .on_conflict_do_nothing(index_elements=["code", "name"])
            )
            result = self._session.execute(stmt)
            return int(result.rowcount or 0)
        except SQLAlchemyError as exc:
            raise StorageError(f"Помилка пакетного запису бюджетів: {exc}") from exc

    def count(self) -> int:
        """Повертає кількість записів у таблиці budgets."""
        stmt = select(func.count()).select_from(BudgetRecord)
        return int(self._session.scalar(stmt) or 0)

    def by_type(self, row_type: str) -> list[BudgetRow]:
        """Повертає список бюджетних записів для заданого типу."""
        stmt = select(BudgetRecord).where(BudgetRecord.type == row_type)
        records = self._session.scalars(stmt).all()
        return [_to_domain(record) for record in records]

    def top_types(self, limit: int = 5) -> list[tuple[str, int]]:
        """Повертає топ типів за кількістю записів."""
        rows = self._session.execute(
            select(BudgetRecord.type, func.count().label("n"))
            .group_by(BudgetRecord.type)
            .order_by(func.count().desc())
            .limit(limit)
        ).all()
        return [(row_type, int(n)) for row_type, n in rows]

    def average_amount(self) -> float | None:
        """Обчислює середнє значення по колонці amount."""
        stmt = select(func.avg(BudgetRecord.amount))
        value = self._session.scalar(stmt)
        return float(value) if value is not None else None
