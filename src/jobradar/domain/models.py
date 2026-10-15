from dataclasses import dataclass

LARGE_ROW_THRESHOLD = 3000

@dataclass(frozen=True, slots=True)
class BudgetRow:
    code: str
    name: str
    amount: int  # Сумма строго int
    type: str

    def __post_init__(self) -> None:
        if not self.code.strip():
            raise ValueError('code must not be empty')
        if not self.name.strip():
            raise ValueError('name must not be empty')
        if self.amount <= 0:
            raise ValueError('amount must be positive')

    @property
    def key(self) -> tuple[str, str]:
        return self.code.strip(), self.name.strip().lower()

    @property
    def is_large_level_transaction(self) -> bool:
        return self.amount >= LARGE_ROW_THRESHOLD
