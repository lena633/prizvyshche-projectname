from collections.abc import Iterator
from typing import Any, Protocol


class Sourse(Protocol):
    name: str

    def read(self) -> Iterator[dict[str, Any]]:
        pass
