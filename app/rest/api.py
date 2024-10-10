from flask import Flask, request, jsonify, Response
from datetime import datetime
from decimal import Decimal
from app.expense_manager.expense_service import ExpenseService
from app.expense_manager.expense_filter import ExpenseFilter
from app.models.expense import Expense
from app.models.category import Category
from app.external.clock import SystemClock
from app.external.database import SQLiteDatabase
import csv
from io import StringIO


app = Flask(__name__)

clock = SystemClock()
database = SQLiteDatabase("expenses.db")
expense_service = ExpenseService(clock, database)


@app.route("/expenses", methods=["POST"])
def create_expense():
    data = request.json
    try:
        expense = Expense(
            amount=Decimal(data["amount"]),
            date=datetime.fromisoformat(data["date"]).date(),
            category=Category(data["category"]),
            description=data.get("description"),
        )
        created_expense = expense_service.create_expense(expense)
        return (
            jsonify(
                {
                    "id": created_expense.id,
                    "amount": str(created_expense.amount),
                    "date": created_expense.date.isoformat(),
                    "category": created_expense.category,
                    "description": created_expense.description,
                }
            ),
            201,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


def get_expenses_json(expenses):
    return jsonify(
        [
            {
                "amount": str(expense.amount),
                "date": expense.date.isoformat(),
                "category": expense.category.value,
                "description": expense.description,
            }
            for expense in expenses
        ]
    )


def get_expenses_csv(expenses):
    csv_data = StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(["Amount", "Date", "Category", "Description"])
    for expense in expenses:
        csv_writer.writerow(
            [
                str(expense.amount),
                expense.date.isoformat(),
                expense.category.value,
                expense.description,
            ]
        )

    response = Response(csv_data.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=expenses.csv"
    return response


@app.route("/expenses", methods=["GET"])
def get_expenses():
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    category = request.args.get("category")

    try:
        expense_filter = ExpenseFilter(
            from_date=datetime.fromisoformat(from_date).date() if from_date else None,
            to_date=datetime.fromisoformat(to_date).date() if to_date else None,
            category=Category(category) if category else None,
        )
        expenses = expense_service.get_expenses_by_filter(expense_filter)

        content_type = request.headers.get("Content-Type", "").lower()

        if content_type == "text/csv":
            return get_expenses_csv(expenses)
        else:
            return get_expenses_json(expenses)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
