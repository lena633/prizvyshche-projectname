import json
import logging
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from ..errors import SourceError

logger = logging.getLogger(__name__)

class JsonlSource:
    name = "jsonl"

    def __init__(self, path: Path) -> None:
        self._path = path

    def read(self) -> Iterator[dict[str, Any]]:
        try:
            handle = self._path.open(encoding="utf-8")
        except OSError as exc:
            raise SourceError(f"cannot open {self._path}") from exc

        with handle as f:
            for number, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    logger.debug("skip malformed line %d in %s", number, self._path)
                    continue
