import argparse
import logging
from collections.abc import Callable
from pathlib import Path

from .config import Settings
from .errors import JobRadarError, SourceError
from .logging_setup import setup
from .services.pipeline import Pipeline, PipelineStats
from .services.ports import Sourse
from .sources.csv_file import CsvSource
from .sources.json_file import JsonlSource
from .storage.db import make_engine, make_session_factory, session_scope
from .storage.models import Base
from .storage.repository import SqlBudgetRepository

logger = logging.getLogger(__name__)

# Регистрация фабрик для Крока 7 из предыдущей лабораторной
FACTORIES: dict[str, Callable[[Path], Sourse]] = {
    ".jsonl": JsonlSource,
    ".csv": CsvSource,
}


def build_source(path: Path) -> Sourse:
    try:
        factory = FACTORIES[path.suffix]
    except KeyError:
        raise SourceError(f"unsupported file type: {path.suffix}") from None
    return factory(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="JobRadar CLI tool")
    parser.add_argument("paths", nargs="+", type=Path, help="Пути к файлам данных")

    # Крок 7: Добавляем флаг --log-level
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="перекриває значення з .env і змінних середовища",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=None,
        help="шлях до файлу бази даних SQLite для збереження результатів",
    )
    return parser


def run_with_storage(sources: list[Sourse], db_path: Path) -> PipelineStats:
    """Створює схему, якщо її немає, і пише потік бюджетних записів у базу."""
    engine = make_engine(db_path)
    Base.metadata.create_all(engine)
    factory = make_session_factory(engine)
    with session_scope(factory) as session:
        return Pipeline(sources).run_into(SqlBudgetRepository(session))


def main() -> None:
    args = build_parser().parse_args()
    settings = Settings()

    # Порядок приоритетов: флаг из CLI перекрывает настройки из .env
    setup(args.log_level or settings.log_level)

    try:
        sources = [build_source(path) for path in args.paths]
        if args.db is not None:
            stats = run_with_storage(sources, args.db)
        else:
            stats = Pipeline(sources).run()
    except JobRadarError as exc:
        # Логируем только понятное сообщение без страшного Traceback для пользователя
        logger.error("%s", exc)
        raise SystemExit(1) from exc

    # Бизнес-ответ пользователю остается в print
    print(f"Прочитано записів: {stats.read}")
    print(f"Відхилено: {stats.invalid}")
    print(f"Дублікатів: {stats.duplicates}")
    print(f"Залишилось: {stats.kept}")
    if args.db is not None:
        print(f"Записано в базу: {stats.written}")
    print("-" * 40)
    print(
        f"Сума видатків: min={stats.amount_min} max={stats.amount_max} avg={stats.amount_avg}"
    )
    print("Розподіл транзакцій за громадами (Топ-5):")
    for community, count in stats.by_community.most_common(5):
        print(f"  {community}: {count}")


if __name__ == "__main__":
    main()
