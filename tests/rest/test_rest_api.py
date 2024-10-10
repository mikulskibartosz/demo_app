import pytest
import json
import csv
from datetime import date, timedelta
from decimal import Decimal
from app.rest.api import app, database
from app.models.category import Category
import os

@pytest.fixture(scope="module")
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="module")
def setup_database():
    yield

    os.remove('expenses.db')


def test_add_expenses(client, setup_database):
    response1 = client.post('/expenses', json={
        'amount': '50.00',
        'date': date.today().isoformat(),
        'category': Category.FOOD.value,
        'description': 'Grocery shopping'
    })
    assert response1.status_code == 201

    response2 = client.post('/expenses', json={
        'amount': '30.00',
        'date': (date.today() - timedelta(days=1)).isoformat(),
        'category': Category.TRANSPORT.value,
        'description': 'Bus ticket'
    })
    assert response2.status_code == 201

    response3 = client.post('/expenses', json={
        'amount': '25.00',
        'date': date.today().isoformat(),
        'category': Category.ENTERTAINMENT.value,
        'description': 'Movie ticket'
    })
    assert response3.status_code == 201


def test_retrieve_without_filter(client, setup_database):
    response = client.get('/expenses')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 3


def test_filter_by_date(client, setup_database):
    yesterday = date.today() - timedelta(days=1)
    response = client.get(f'/expenses?from_date={yesterday.isoformat()}&to_date={yesterday.isoformat()}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert Decimal(data[0]['amount']) == Decimal('30.00')
    assert data[0]['category'] == Category.TRANSPORT.value


def test_filter_by_category(client, setup_database):
    response = client.get(f'/expenses?category={Category.FOOD.value}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert Decimal(data[0]['amount']) == Decimal('50.00')
    assert data[0]['category'] == Category.FOOD.value


def test_retrieve_as_csv(client, setup_database):
    response = client.get('/expenses', headers={'Content-Type': 'text/csv'})
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/csv; charset=utf-8'
    assert response.headers['Content-Disposition'] == 'attachment; filename=expenses.csv'

    csv_data = response.data.decode('utf-8')
    csv_reader = csv.reader(csv_data.splitlines())
    rows = list(csv_reader)
    assert len(rows) == 4  # Header + 3 expenses
    assert rows[0] == ['Amount', 'Date', 'Category', 'Description']
    assert Decimal(rows[1][0]) == Decimal('50.00')
    assert Decimal(rows[2][0]) == Decimal('30.00')
    assert Decimal(rows[3][0]) == Decimal('25.00')
