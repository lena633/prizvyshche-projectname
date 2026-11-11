import logging  # Модуль журналирования
import sys  # Доступ к системным потокам


def setup(level: str = "INFO") -> None:
    logging.basicConfig(
        level=level.upper(),  # Устанавливаем уровень сообщений
        format="%(asctime)s %(levelname)-8s %(name)s | %(message)s",
        # Формат: время, уровень, название модуля и сообщение
        datefmt="%H:%M:%S",  # Формат отображения времени
        stream=sys.stdout,  # Выводим журнал в консоль
    )
