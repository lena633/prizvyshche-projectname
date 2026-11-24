"""Тести SQLAlchemy-репозиторію SqlBudgetRepository на тимчасовій базі."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from jobradar.domain.models import BudgetRow
from jobradar.storage.db import make_engine, make_session_factory
from jobradar.storage.models import Base
from jobradar.storage.repository import SqlBudgetRepository


@pytest.fixture
def session(tmp_path: Path) -> Iterator[Session]:
    """Порожня база на один тест – у тимчасовому каталозі, не в проєкті."""
    engine = make_engine(tmp_path / "test.db")
    Base.metadata.create_all(engine)
    factory = make_session_factory(engine)
    db = factory()
    yield db
    db.close()
    engine.dispose()


def _make_row(
    code: str = "0111010",
    name: str = "Оплата праці",
    amount: int = 5000,
    row_type: str = "Видатки",
) -> BudgetRow:
    return BudgetRow(code=code, name=name, amount=amount, type=row_type)


def test_empty_storage(session: Session) -> None:
    repo = SqlBudgetRepository(session)
    assert repo.count() == 0
    assert repo.by_type("Видатки") == []
    assert repo.top_types() == []
    assert repo.average_amount() is None


def test_add_many_and_idempotency(session: Session) -> None:
    repo = SqlBudgetRepository(session, batch_size=2)
    rows = [
        _make_row(
            code="0111010", name="Зарплата", amount=10000, row_type="Загальний фонд"
        ),
        _make_row(
            code="0111020", name="Нарахування", amount=2200, row_type="Загальний фонд"
        ),
        _make_row(
            code="0112010", name="Обладнання", amount=15000, row_type="Спеціальний фонд"
        ),
    ]

    written_first = repo.add_many(rows)
    session.commit()
    assert written_first == 3
    assert repo.count() == 3

    written_second = repo.add_many(rows)
    session.commit()
    assert written_second == 0
    assert repo.count() == 3


def test_duplicate_inside_single_batch(session: Session) -> None:
    repo = SqlBudgetRepository(session, batch_size=10)
    rows = [
        _make_row(code="0111010", name="Комунальні послуги", amount=4000),
        _make_row(code="0111010", name="Комунальні послуги", amount=4000),
    ]

    written = repo.add_many(rows)
    session.commit()
    assert written == 1
    assert repo.count() == 1


def test_same_name_different_code_is_distinct_row(session: Session) -> None:
    repo = SqlBudgetRepository(session)
    rows = [
        _make_row(code="0111010", name="Оплата електроенергії", amount=3000),
        _make_row(code="0112010", name="Оплата електроенергії", amount=7000),
    ]

    written = repo.add_many(rows)
    session.commit()
    assert written == 2
    assert repo.count() == 2


def test_by_type_and_top_types_sorting(session: Session) -> None:
    repo = SqlBudgetRepository(session)
    rows = [
        _make_row(code="1", name="Рядок 1", amount=1000, row_type="Доходи"),
        _make_row(code="2", name="Рядок 2", amount=2000, row_type="Видатки"),
        _make_row(code="3", name="Рядок 3", amount=3000, row_type="Видатки"),
        _make_row(code="4", name="Рядок 4", amount=4000, row_type="Видатки"),
        _make_row(code="5", name="Рядок 5", amount=5000, row_type="Кредитування"),
        _make_row(code="6", name="Рядок 6", amount=6000, row_type="Кредитування"),
    ]
    repo.add_many(rows)
    session.commit()

    expenses = repo.by_type("Видатки")
    assert len(expenses) == 3
    assert all(r.type == "Видатки" for r in expenses)

    top = repo.top_types(limit=2)
    assert top == [("Видатки", 3), ("Кредитування", 2)]


def test_average_amount(session: Session) -> None:
    repo = SqlBudgetRepository(session)
    rows = [
        _make_row(code="1", name="А", amount=1000),
        _make_row(code="2", name="Б", amount=3000),
    ]
    repo.add_many(rows)
    session.commit()

    assert repo.average_amount() == pytest.approx(2000.0)
