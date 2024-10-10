"""Expense Manager Module

This module provides functionality for managing expenses through the ExpenseService class.

The ExpenseService class interacts with the Clock and Database abstractions to handle
time-related operations and data persistence, respectively. It also uses the ExpenseFilter
class to filter expenses based on various criteria.

Classes:
    ExpenseService: A service class for managing expenses.
    ExpenseFilter: A class for filtering expenses based on date range and category.

Interactions:
    - Clock (@clock.py):
        The ExpenseService uses a Clock instance to get the current time for validating
        expense dates. It ensures that expenses are not created with future dates.

    - Database (@database.py):
        The ExpenseService uses a Database instance to persist and retrieve expense data.
        It interacts with the database to save new expenses and retrieve existing ones
        based on filter criteria.

    - ExpenseFilter (@expense_filter.py):
        The ExpenseService uses ExpenseFilter to filter expenses based on date range
        and category.

Usage:
    from app.expense_manager import ExpenseService
    from app.external.clock import SystemClock
    from app.external.database import SQLiteDatabase
    from app.expense_manager.expense_filter import ExpenseFilter

    clock = SystemClock()
    database = SQLiteDatabase('expenses.db')
    expense_service = ExpenseService(clock, database)

    # Create an expense
    expense = Expense(amount=Decimal("50.00"), date=date(2023, 4, 15), category=Category.FOOD, description="Groceries")
    expense_service.create_expense(expense)

    # Get expenses by filter
    expense_filter = ExpenseFilter(from_date=date(2023, 1, 1), to_date=date(2023, 12, 31), category=Category.FOOD)
    filtered_expenses = expense_service.get_expenses_by_filter(expense_filter)
"""
