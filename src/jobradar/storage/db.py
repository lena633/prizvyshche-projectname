from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from jobradar.errors import StorageError
from jobradar.storage.models import Base


def make_engine(path: Path, echo: bool = False) -> Engine:
    """Створює двигун SQLite та примусово вмикає перевірку зовнішніх ключів."""
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{path}", echo=echo, future=True)

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(connection: Any, _record: Any) -> None:
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def init_db(engine: Engine) -> None:
    """Створює всі таблиці в базі даних на основі метаданих Base."""
    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as exc:
        raise StorageError(f"Не вдалося ініціалізувати схему БД: {exc}") from exc


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Повертає налаштовану фабрику сесій."""
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@contextmanager
def session_scope(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    """Контекстний менеджер транзакції з автоматичним commit/rollback."""
    session = session_factory()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as exc:
        session.rollback()
        raise StorageError(f"Помилка транзакції бази даних: {exc}") from exc
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
