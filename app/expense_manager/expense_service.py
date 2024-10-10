from typing import List
from app.external.clock import Clock
from app.models.expense import Expense, MAX_DESCRIPTION_LENGTH
from app.models.category import Category
from app.external.database import Database
from app.expense_manager.expense_filter import ExpenseFilter


class ExpenseService:
    """A service class for managing expenses.

    This class provides methods for creating and managing expenses.

    Attributes:
        clock (Clock): An instance of Clock for time-related operations.
        database (Database): An instance of Database for data persistence.
    """

    def __init__(self, clock: Clock, database: Database):
        """Initialize the ExpenseService.

        Args:
            clock (Clock): An instance of Clock for time-related operations.
            database (Database): An instance of Database for data persistence.
        """
        self.clock = clock
        self.database = database

    def create_expense(self, expense: Expense):
        """Create a new expense.

        This method validates the expense and saves it to the database.

        Args:
            expense (Expense): The expense to be created.

        Returns:
            DbExpense: The created expense as returned by the database.

        Raises:
            ValueError: If the expense is invalid (negative amount, future date,
                        description too long, or invalid category).
        """
        if expense.amount <= 0:
            raise ValueError("Amount must be positive")
        if expense.date > self.clock.now().date():
            raise ValueError("Date cannot be in the future")
        if (
            expense.description is not None
            and len(expense.description) > MAX_DESCRIPTION_LENGTH
        ):
            raise ValueError("Description cannot be longer than 255 characters")
        if not isinstance(expense.category, Category):
            raise ValueError("Invalid category")

        db_expense = self.database.save_expense(expense)
        return db_expense

    def get_expenses_by_filter(self, filter: ExpenseFilter) -> List[Expense]:
        """Get expenses that match the given filter.

        Args:
            filter (ExpenseFilter): The filter to apply to the expenses.

        Returns:
            List[Expense]: A list of expenses that match the filter.

        Raises:
            ValueError: If the filter is invalid (e.g., from_date is after to_date).
        """
        if filter.from_date and filter.to_date and filter.from_date > filter.to_date:
            raise ValueError("from_date cannot be after to_date")

        category_filter = filter.category.value if filter.category else None
        db_expenses = self.database.find_expenses_by_filter(
            filter.from_date, filter.to_date, category_filter
        )
        expenses = [Expense.from_db_expense(db_expense) for db_expense in db_expenses]
        return expenses
