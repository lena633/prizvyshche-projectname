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
        help="перекриває значення з .env і змінних середовища"
    )
    return parser

def main() -> None:
    args = build_parser().parse_args()
    settings = Settings()
    
    # Порядок приоритетов: флаг из CLI перекрывает настройки из .env
    setup(args.log_level or settings.log_level)
    
    try:
        sources = [build_source(path) for path in args.paths]
        stats: PipelineStats = Pipeline(sources).run()
    except JobRadarError as exc:
        # Логируем только понятное сообщение без страшного Traceback для пользователя
        logger.error("%s", exc)
        raise SystemExit(1) from exc

    # Бизнес-ответ пользователю остается в print
    print(f"Прочитано записів: {stats.read}")
    print(f"Відхилено: {stats.invalid}")
    print(f"Дублікатів: {stats.duplicates}")
    print(f"Залишилось: {stats.kept}")
    print("-" * 40)
    print(f"Сума видатків: min={stats.amount_min} max={stats.amount_max} avg={stats.amount_avg}")
    print("Розподіл транзакцій за громадами (Топ-5):")
    for community, count in stats.by_community.most_common(5):
        print(f"  {community}: {count}")

if __name__ == "__main__":
    main()
