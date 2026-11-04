from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..domain.models import BudgetRow


class BudgetIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    code: str = Field(min_length=1, max_length=200)
    name: str = Field(min_length=1)
    amount: int = Field(gt=0)
    type: str = Field(default='', alias='location')

    @field_validator('amount', mode='before')
    @classmethod
    def unknown_amount(cls, value: Any) -> Any:
        if isinstance(value, str):
            cleaned = value.strip()
            try:
                return int(cleaned)
            except ValueError:
                return -1  # Специальное некорректное число для вызова ValidationError
        return value

    @field_validator("code", "name")
    @classmethod
    def strip_spaces(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("code")
    @classmethod
    def lowercase(cls, value: str) -> str:
        return value.lower()

    def to_domain(self) -> BudgetRow:
        return BudgetRow(
            code=self.code,
            name=self.name,
            amount=self.amount,
            type=self.type
        )
