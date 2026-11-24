"""ORM-моделі таблиць сховища JobRadar."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовий декларативний клас для всіх моделей."""


class BudgetRecord(Base):
    """Рядок таблиці бюджетних записів у базі даних SQLite."""

    __tablename__ = "budgets"

    code: Mapped[str] = mapped_column(String(255), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), primary_key=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    def __repr__(self) -> str:
        return (
            f"<BudgetRecord(code={self.code!r}, name={self.name!r}, "
            f"amount={self.amount!r}, type={self.type!r})>"
        )
