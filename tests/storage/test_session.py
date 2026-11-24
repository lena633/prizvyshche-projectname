"""Тести двигуна БД, зовнішніх ключів та межі транзакції session_scope."""

from pathlib import Path

import pytest
from sqlalchemy import text

from jobradar.domain.models import BudgetRow
from jobradar.errors import StorageError
from jobradar.storage.db import (
    init_db,
    make_engine,
    make_session_factory,
    session_scope,
)
from jobradar.storage.models import Base
from jobradar.storage.repository import SqlBudgetRepository


def test_foreign_keys_enabled(tmp_path: Path) -> None:
    """SQLite має вмикати PRAGMA foreign_keys=ON при кожному підключенні."""
    engine = make_engine(tmp_path / "fk.db")
    with engine.connect() as conn:
        fk_status = conn.execute(text("PRAGMA foreign_keys")).scalar()
    engine.dispose()
    assert fk_status == 1


def test_session_scope_commits_changes(tmp_path: Path) -> None:
    """Успішне завершення session_scope зберігає дані у базу."""
    engine = make_engine(tmp_path / "commit.db")
    init_db(engine)
    factory = make_session_factory(engine)

    with session_scope(factory) as session:
        repo = SqlBudgetRepository(session)
        repo.add_many(
            [BudgetRow(code="0111010", name="Зарплата", amount=5000, type="Видатки")]
        )

    with session_scope(factory) as session:
        assert SqlBudgetRepository(session).count() == 1

    engine.dispose()


def test_failed_transaction_rolls_everything_back(tmp_path: Path) -> None:
    """Помилка в середині транзакції не має лишити половину записів."""
    engine = make_engine(tmp_path / "rollback.db")
    Base.metadata.create_all(engine)
    factory = make_session_factory(engine)

    with (
        pytest.raises(StorageError, match="transaction failed"),
        session_scope(factory) as session,
    ):
        SqlBudgetRepository(session).add_many(
            [BudgetRow(code="0111010", name="Тест", amount=500, type="Видатки")]
        )
        raise RuntimeError("щось пішло не так уже після запису")

    with session_scope(factory) as session:
        assert SqlBudgetRepository(session).count() == 0

    engine.dispose()
