from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BudgetRow:
    code: str
    name: str
    amount: int | None
    type: str  # income или expense

    @property
    def key(self) -> tuple[str, str]:
        # Уникальный ключ для дедупликации на основе кода и названия статьи
        return self.code, self.name
