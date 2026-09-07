# Employee Compensation Service (Python)

Azure Functions (HTTP-triggered, Python v2 programming model) backend for
managing Employee/Department records and answering bonus-reporting
questions, backed by Azure SQL / SQL Server via `pyodbc`. All reads and
writes go through the Functions layer - there is no direct database access
from clients.

## Tech stack

- **Runtime:** Azure Functions v4, Python 3, v2 programming model (Blueprints)
- **Database:** Azure SQL Database (or any SQL Server instance) via `pyodbc`, parameterized `?`-style queries throughout (no string-built SQL)
- **Tests:** `pytest`, for the pure validation logic

## Project layout

```
sql/                                  CREATE TABLE + seed scripts
db/connection.py                      Small thread-safe pyodbc connection pool; config from env vars only
utils/
  errors.py                           AppError — zero dependencies, so validation stays framework-free
  http_helpers.py                     Response helpers + centralized error handling
  validation.py                       Request body/param validation
repositories/
  employee_repository.py              Part A CRUD queries
  reports_repository.py               Part B reporting queries
functions/                            Part A HTTP endpoints (one Blueprint per file)
functions/reports/                    Part B HTTP endpoints
function_app.py                       Registers every Blueprint with the Functions host
tests/test_validation.py              Unit tests for validation logic
```

## Setup & running locally

1. **Prerequisites:**
   - Python 3
   - [Azure Functions Core Tools v4](https://learn.microsoft.com/azure/azure-functions/functions-run-local)
   - The **ODBC Driver 17 for SQL Server** installed on your machine (`pyodbc` talks to SQL Server through it, not directly) — see [Microsoft's install docs](https://learn.microsoft.com/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server) for your OS.
   - Access to a SQL Server / Azure SQL instance.

2. **Create the schema and seed data**, in order, against your database:

   ```
   sql/01_create_tables.sql
   sql/02_seed_data.sql
   ```

3. **Configure local settings.** Copy the example file — it's git-ignored and never committed:

   ```bash
   cp local.settings.json.example local.settings.json
   ```

   Fill in `SQL_SERVER`, `SQL_DATABASE`, `SQL_USER`, `SQL_PASSWORD`. `SQL_DRIVER` defaults to `{ODBC Driver 18 for SQL Server}` — adjust if you installed a different driver name. `DEFAULT_BONUS_RATE` (default `0.05`) controls the optional Part C default-bonus feature.

4. **Create a virtual environment and install dependencies:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # .venv\Scripts\activate on Windows
   pip install -r requirements.txt -r requirements-dev.txt
   ```

5. **Run it:**

   ```bash
   func start
   ```

   The API will be available at `http://localhost:7071/api/...`.

6. **Run the unit tests:**
   ```bash
   pytest
   ```

## API reference

### Part A — Data access (CRUD)

| Method   | Route                              | Description                                                                                           |
| -------- | ---------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `POST`   | `/api/employees`                   | Create an employee. Body: `firstName, lastName, departmentId, salary, hireDate` and optional `bonus`. |
| `GET`    | `/api/employees/{id}`              | Get a single employee by ID. `404` if not found.                                                      |
| `GET`    | `/api/employees?departmentId={id}` | List employees, optionally filtered by department.                                                    |
| `PUT`    | `/api/employees/{id}`              | Partial update — send only the fields that change.                                                    |
| `DELETE` | `/api/employees/{id}`              | Delete an employee. Returns `204`.                                                                    |

### Part B — Compensation reporting

| Method | Route                                               | Description                                                                                          |
| ------ | --------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `GET`  | `/api/reports/total-bonus`                          | Total bonus paid company-wide (`NULL` treated as 0). Optional `?applyDefaultBonus=true` (see below). |
| `GET`  | `/api/reports/employees-without-bonus`              | Employees who have never received a bonus.                                                           |
| `GET`  | `/api/reports/bonus-percentage`                     | For each employee **with** a bonus, bonus as % of salary, rounded to 2 dp.                           |
| `GET`  | `/api/reports/departments-bonus-exceeds-avg-salary` | Departments where total bonus paid > that department's average salary.                               |
| `GET`  | `/api/reports/employees-ranked-by-bonus`            | All employees ranked by bonus, descending; no-bonus employees ranked last (not excluded).            |
| `GET`  | `/api/reports/highest-salary-employee`              | Highest base-salary employee, and whether they also have the highest total compensation.             |

All endpoints return JSON and appropriate status codes (`200`, `201`, `204`, `400` for validation errors, `404` for missing resources, `500` for unexpected failures).

## Notes & Design Decisions

- Notes & Design Decisions
- PUT supports partial updates.
- Salary and bonus cannot be negative.
- NULL bonus means the employee has no recorded bonus.
- NULL bonuses are treated as 0 for calculations.
- Employees with no bonus are ranked last.
- Ties are resolved using the lowest EmployeeID.
- All SQL queries use parameters to prevent SQL injection.
- Validation errors return 400, missing employees return 404, and unexpected errors return 500.
- Database credentials are loaded from environment variables.
- A thread-safe connection pool is used for concurrent requests.
- The optional 5% default bonus is calculated at read time and is not stored in the database. This preserves the - distinction between an employee with no bonus and an employee who received a bonus.
