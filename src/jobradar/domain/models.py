from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BudgetRow:
    code: str
    name: str
    amount: str
    type: str

    @property
    def key(self) -> tuple[str, str]:
        # Очищаем от пробелов и приводим к нижнему регистру для стабильности тестов
        return self.code.strip(), self.name.strip().lower()


@dataclass(frozen=True)
class Income:
    income: str


@dataclass(frozen=True)
class Expenses:
    expenses: str
