import pytest
from datetime import datetime, timezone, timedelta
from app.external.database import SQLiteDatabase, MockDatabase
from app.external.clock import MockClock
from app.expense_manager.expense_service import ExpenseService
from app.expense_manager.expense_filter import ExpenseFilter
from app.models.expense import Expense
from app.models.category import Category
from decimal import Decimal


EXPENSE_DATE = datetime(2023, 4, 15, tzinfo=timezone.utc)
EXPENSE_FOOD_AMOUNT = Decimal("50.00")
EXPENSE_TRANSPORT_AMOUNT = Decimal("100.00")
EXPENSE_FOOD_AMOUNT_2 = Decimal("150.00")


@pytest.fixture
def mock_clock():
    return MockClock(datetime(2024, 10, 10, 8, 0, tzinfo=timezone.utc))


@pytest.fixture()
def database(request):
    database_type = request.config.getoption("--database")
    if database_type == "sqlite":
        return SQLiteDatabase(":memory:")
    return MockDatabase()


@pytest.fixture()
def expense_service(mock_clock, database):
    return ExpenseService(mock_clock, database)


@pytest.fixture()
def mock_data(database):
    database.save_expense(
        Expense(
            amount=EXPENSE_FOOD_AMOUNT,
            date=EXPENSE_DATE,
            category=Category.FOOD,
            description="Food expense",
        )
    )
    database.save_expense(
        Expense(
            amount=EXPENSE_TRANSPORT_AMOUNT,
            date=EXPENSE_DATE,
            category=Category.TRANSPORT,
            description="Transport expense",
        )
    )
    database.save_expense(
        Expense(
            amount=EXPENSE_FOOD_AMOUNT_2,
            date=EXPENSE_DATE,
            category=Category.FOOD,
            description="Food expense",
        )
    )

    return database


def test_list_expenses_no_filter(mock_data, expense_service):
    expenses = expense_service.get_expenses_by_filter(ExpenseFilter())
    assert len(expenses) == 3


def test_list_expenses_date_range_with_exact_date(mock_data, expense_service):
    filter = ExpenseFilter(from_date=EXPENSE_DATE, to_date=EXPENSE_DATE)
    expenses = expense_service.get_expenses_by_filter(filter)
    assert len(expenses) == 3


def test_list_expenses_date_range_with_start_date(mock_data, expense_service):
    filter = ExpenseFilter(from_date=EXPENSE_DATE)
    expenses = expense_service.get_expenses_by_filter(filter)
    assert len(expenses) == 3


def test_list_expenses_date_range_with_end_date(mock_data, expense_service):
    filter = ExpenseFilter(to_date=EXPENSE_DATE)
    expenses = expense_service.get_expenses_by_filter(filter)
    assert len(expenses) == 3


def test_list_expenses_date_range_with_empty_result_after_start_date(
    mock_data, expense_service
):
    filter = ExpenseFilter(from_date=datetime(2023, 4, 16, tzinfo=timezone.utc))
    expenses = expense_service.get_expenses_by_filter(filter)
    assert len(expenses) == 0


def test_list_expenses_date_range_with_empty_result_before_end_date(
    mock_data, expense_service
):
    filter = ExpenseFilter(to_date=datetime(2023, 4, 14, tzinfo=timezone.utc))
    expenses = expense_service.get_expenses_by_filter(filter)
    assert len(expenses) == 0


def test_list_expenses_category_filter(mock_data, expense_service):
    filter = ExpenseFilter(category=Category.FOOD)
    expenses = expense_service.get_expenses_by_filter(filter)
    assert len(expenses) == 2


def test_list_expenses_category_filter_with_empty_result(mock_data, expense_service):
    filter = ExpenseFilter(category=Category.OTHER)
    expenses = expense_service.get_expenses_by_filter(filter)
    assert len(expenses) == 0


def test_list_expenses_date_range_and_category_filter(mock_data, expense_service):
    filter = ExpenseFilter(
        from_date=EXPENSE_DATE, to_date=EXPENSE_DATE, category=Category.TRANSPORT
    )
    expenses = expense_service.get_expenses_by_filter(filter)
    assert len(expenses) == 1


def test_list_expenses_invalid_date_range(mock_data, expense_service):
    filter = ExpenseFilter(
        from_date=EXPENSE_DATE, to_date=EXPENSE_DATE - timedelta(days=1)
    )
    with pytest.raises(ValueError):
        expense_service.get_expenses_by_filter(filter)
