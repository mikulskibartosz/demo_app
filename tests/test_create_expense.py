import pytest
from datetime import date, datetime, timezone
from decimal import Decimal
from app.models.expense import Expense, MAX_DESCRIPTION_LENGTH
from app.models.category import Category
from app.expense_manager.expense_service import ExpenseService
from app.external.clock import MockClock
from app.external.database import MockDatabase, SQLiteDatabase, Database


class DbAssertObject:
    def __init__(self, database: Database):
        self.database = database

    def assert_last_expense(self, expected_expense: Expense):
        assert (
            self.database.get_expense_count() > 0
        ), "No expense was inserted into the database"
        last_expense = self.database.get_last_expense()
        assert last_expense is not None
        assert last_expense.amount == expected_expense.amount
        assert last_expense.date == expected_expense.date
        assert last_expense.category == expected_expense.category.value
        assert last_expense.description == expected_expense.description

    def assert_no_expense_inserted(self):
        assert (
            self.database.get_expense_count() == 0
        ), "An unexpected expense was inserted into the database"


@pytest.fixture
def db_assert(database):
    return DbAssertObject(database)


@pytest.fixture
def mock_clock():
    return MockClock(datetime(2024, 10, 10, 8, 0, tzinfo=timezone.utc))


# To use SQLiteDatabase, run pytest with: pytest --database-type=sqlite
# To use MockDatabase (default), run pytest with: pytest
# or explicitly with: pytest --database-type=mock
@pytest.fixture()
def database(request):
    database_type = request.config.getoption("--database")
    if database_type == "sqlite":
        return SQLiteDatabase(":memory:")
    return MockDatabase()


@pytest.fixture()
def expense_service(mock_clock, database):
    return ExpenseService(mock_clock, database)


@pytest.mark.parametrize(
    "category", [pytest.param(category, id=category.value) for category in Category]
)
def test_create_expense_success(expense_service, category, db_assert):
    amount = Decimal("50.00")
    test_date = date(2023, 4, 15)
    description = f"{category.value} expense"

    expense = Expense(
        amount=amount, date=test_date, category=category, description=description
    )

    expense_service.create_expense(expense)

    db_assert.assert_last_expense(expense)


def test_create_expense_negative_amount(expense_service, db_assert):
    with pytest.raises(ValueError):
        expense = Expense(
            amount=Decimal("-10.00"),
            date=date(2023, 4, 15),
            category=Category.FOOD,
            description="Invalid negative amount",
        )
        expense_service.create_expense(expense)

    db_assert.assert_no_expense_inserted()


def test_create_expense_future_date(expense_service, db_assert):
    future_date = date(2024, 10, 11)  # One day after the mock clock date
    with pytest.raises(ValueError):
        expense = Expense(
            amount=Decimal("30.00"),
            date=future_date,
            category=Category.TRANSPORT,
            description="Future expense",
        )
        expense_service.create_expense(expense)

    db_assert.assert_no_expense_inserted()


def test_create_expense_invalid_category(expense_service, db_assert):
    with pytest.raises(ValueError):
        expense = Expense(
            amount=Decimal("100.00"),
            date=date(2023, 4, 15),
            category="Invalid Category",
            description="Expense with invalid category",
        )
        expense_service.create_expense(expense)

    db_assert.assert_no_expense_inserted()


def test_create_expense_empty_description(expense_service, db_assert):
    expense = Expense(
        amount=Decimal("25.00"),
        date=date(2023, 4, 15),
        category=Category.ENTERTAINMENT,
        description="",
    )

    expense_service.create_expense(expense)

    db_assert.assert_last_expense(expense)


def test_create_expense_long_description(expense_service, db_assert):
    long_description = "A" * (MAX_DESCRIPTION_LENGTH + 1)
    with pytest.raises(ValueError):
        expense = Expense(
            amount=Decimal("75.00"),
            date=date(2023, 4, 15),
            category=Category.OTHER,
            description=long_description,
        )
        expense_service.create_expense(expense)

    db_assert.assert_no_expense_inserted()
