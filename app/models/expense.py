from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional
from app.models.category import Category


MAX_DESCRIPTION_LENGTH = 255


@dataclass
class Expense:
    amount: Decimal
    date: date
    category: Category
    description: Optional[str] = None

    @classmethod
    def from_db_expense(cls, db_expense):
        return cls(
            amount=db_expense.amount,
            date=db_expense.date,
            category=Category(db_expense.category),
            description=db_expense.description,
        )
