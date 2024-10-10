# Expense Tracker API

This application is an Expense Tracker API built with Flask. It allows users to create, retrieve, and filter expenses. The API supports both JSON and CSV formats for data retrieval, making it versatile for various client needs.

## Running Tests

To run the tests, you can use the following commands:

1. To run tests with MockDatabase (default):
   ```
   poetry run pytest
   ```

2. To run tests with SQLite in-memory database:
   ```
   poetry run pytest --database-type=sqlite
   ```

## Running the Application

To run the application, use the following command:

```
poetry run python -m app.rest.api
```

## API Endpoints

### Create Expense


- **URL**: `/expenses`
- **Method**: `POST`
- **Data Params**:
  ```json
  {
    "amount": "50.00",
    "date": "2023-05-20",
    "category": "Food",
    "description": "Grocery shopping"
  }
  ```
- **Success Response**:
  - **Code**: 201
  - **Content**:
    ```json
    {
      "id": 1,
      "amount": "50.00",
      "date": "2023-05-20",
      "category": "Food",
      "description": "Grocery shopping"
    }
    ```
- **Error Response**:
  - **Code**: 400
  - **Content**: `{"error": "Invalid data provided"}`

### Retrieve Expenses

- **URL**: `/expenses`
- **Method**: `GET`
- **URL Params**:
  - `from_date` (optional): Start date for filtering (format: YYYY-MM-DD)
  - `to_date` (optional): End date for filtering (format: YYYY-MM-DD)
  - `category` (optional): Category to filter by
- **Headers**:
  - `Content-Type`: `application/json` (default) or `text/csv`
- **Success Response**:
  - **Code**: 200
  - **Content**:
    - JSON format (default):
      ```json
      [
        {
          "amount": "50.00",
          "date": "2023-05-20",
          "category": "Food",
          "description": "Grocery shopping"
        },
        {
          "amount": "30.00",
          "date": "2023-05-19",
          "category": "Transport",
          "description": "Bus ticket"
        }
      ]
      ```
    - CSV format (when `Content-Type: text/csv` is specified):
      ```
      Amount,Date,Category,Description
      50.00,2023-05-20,Food,Grocery shopping
      30.00,2023-05-19,Transport,Bus ticket
      ```
- **Error Response**:
  - **Code**: 400
  - **Content**: `{"error": "Invalid filter parameters"}`


### Curl examples

1. Create an expense:
    ```
    curl -X POST http://localhost:5000/expenses -H "Content-Type: application/json" -d '{"amount": "50.00", "date": "2023-05-20", "category": "Food", "description": "Grocery shopping"}'
    ```

2. Retrieve expenses with JSON format:
    ```
    curl http://localhost:5000/expenses
    ```

3. Retrieve expenses with CSV format:
    ```
    curl http://localhost:5000/expenses -H "Accept: text/csv"
    ```

