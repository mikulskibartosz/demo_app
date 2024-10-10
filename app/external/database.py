from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional
import sqlite3


@dataclass
class DbExpense:
    id: int
    amount: Decimal
    date: date
    category: str
    description: Optional[str] = None


class Database(ABC):
    @abstractmethod
    def save_expense(self, expense) -> DbExpense:
        pass

    @abstractmethod
    def get_last_expense(self) -> Optional[DbExpense]:
        pass

    @abstractmethod
    def get_expense_count(self) -> int:
        pass

    @abstractmethod
    def find_expenses_by_filter(
        self,
        from_date: Optional[date],
        to_date: Optional[date],
        category: Optional[str],
    ) -> list[DbExpense]:
        pass


class MockDatabase(Database):
    def __init__(self):
        self.expenses = []

    def save_expense(self, expense) -> DbExpense:
        db_expense = DbExpense(
            id=len(self.expenses) + 1,
            amount=expense.amount,
            date=expense.date,
            category=expense.category.value,
            description=expense.description,
        )
        self.expenses.append(db_expense)
        return db_expense

    def get_last_expense(self) -> Optional[DbExpense]:
        return self.expenses[-1] if self.expenses else None

    def get_expense_count(self) -> int:
        return len(self.expenses)

    def find_expenses_by_filter(
        self,
        from_date: Optional[date],
        to_date: Optional[date],
        category: Optional[str],
    ) -> list[DbExpense]:
        def predicate(expense):
            if from_date and expense.date < from_date:
                return False
            if to_date and expense.date > to_date:
                return False
            if category and expense.category != category:
                return False
            return True

        return [expense for expense in self.expenses if predicate(expense)]


class SQLiteDatabase(Database):
    def __init__(self, db_file="database.db"):
        self.db_file = db_file
        self.use_in_memory_connection = db_file == ":memory:"
        self.connection = (
            sqlite3.connect(self.db_file) if self.use_in_memory_connection else None
        )
        self._create_table()

    def _connect(self):
        if self.connection:
            return self.connection
        return sqlite3.connect(self.db_file)

    def close(self, conn):
        if not self.use_in_memory_connection:
            conn.close()

    def _create_table(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount DECIMAL(10, 2) NOT NULL,
                date DATE NOT NULL,
                category TEXT NOT NULL,
                description TEXT
            )
        """
        )
        conn.commit()
        self.close(conn)

    def save_expense(self, expense) -> DbExpense:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO expenses (amount, date, category, description)
            VALUES (?, ?, ?, ?)
        """,
            (
                str(expense.amount),
                expense.date.isoformat(),
                expense.category.value,
                expense.description,
            ),
        )
        expense_id = cursor.lastrowid
        conn.commit()
        self.close(conn)

        return DbExpense(
            id=expense_id,
            amount=expense.amount,
            date=expense.date,
            category=expense.category.value,
            description=expense.description,
        )

    def get_last_expense(self) -> Optional[DbExpense]:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, amount, date, category, description
            FROM expenses
            ORDER BY id DESC
            LIMIT 1
        """
        )
        result = cursor.fetchone()
        self.close(conn)

        if result:
            return DbExpense(
                id=result[0],
                amount=Decimal(result[1]),
                date=date.fromisoformat(result[2]),
                category=result[3],
                description=result[4],
            )
        return None

    def get_expense_count(self) -> int:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM expenses")
        count = cursor.fetchone()[0]
        self.close(conn)
        return count

    def find_expenses_by_filter(
        self,
        from_date: Optional[date],
        to_date: Optional[date],
        category: Optional[str],
    ) -> list[DbExpense]:
        conn = self._connect()
        cursor = conn.cursor()
        query = "SELECT id, amount, date, category, description FROM expenses WHERE 1"
        params = []

        if from_date:
            query += " AND date >= ?"
            params.append(from_date.isoformat())
        if to_date:
            query += " AND date <= ?"
            params.append(to_date.isoformat())
        if category:
            query += " AND category = ?"
            params.append(category)

        cursor.execute(query, params)
        results = cursor.fetchall()
        self.close(conn)

        return [
            DbExpense(
                id=result[0],
                amount=Decimal(result[1]),
                date=date.fromisoformat(result[2]),
                category=result[3],
                description=result[4],
            )
            for result in results
        ]
