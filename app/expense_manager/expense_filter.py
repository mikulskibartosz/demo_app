from dataclasses import dataclass
from datetime import date
from typing import Optional
from app.models.category import Category


@dataclass
class ExpenseFilter:
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    category: Optional[Category] = None
