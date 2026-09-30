from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Vacancy:
    title: str
    company: str
    salary: int | None
    city: str

    @property
    def key(self) -> tuple[str, str]:
        return self.title, self.company
