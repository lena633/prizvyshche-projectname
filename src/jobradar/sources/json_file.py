import json  # Работа с JSON-данными
import logging  # Запись сообщений в журнал
from collections.abc import Iterator  # Тип для последовательной выдачи данных
from pathlib import Path  # Работа с путями к файлам
from typing import Any  # Разрешает значения разных типов

from ..errors import SourceError  # Собственная ошибка источника данных

logger = logging.getLogger(__name__)  # Создаём журнал для этого файла


class JsonlSource:
    name = "jsonl"  # Название источника данных

    def __init__(self, path: Path) -> None:
        self._path = path  # Сохраняем путь к файлу

    def read(self) -> Iterator[dict[str, Any]]:
        try:
            handle = self._path.open(encoding="utf-8")  # Открываем файл
        except OSError as exc:
            # Если файл не удалось открыть, вызываем собственную ошибку
            raise SourceError(f"cannot open {self._path}") from exc

        with handle as f:  # Автоматически закрываем файл после чтения
            for number, line in enumerate(f, start=1):  # Читаем файл построчно
                if not line.strip():  # Проверяем, пустая ли строка
                    continue  # Пропускаем пустую строку

                try:
                    yield json.loads(line)  # Преобразуем JSON в словарь Python
                except json.JSONDecodeError:
                    # Записываем информацию о некорректной строке
                    logger.debug("skip malformed line %d in %s", number, self._path)
                    continue  # Переходим к следующей строке
