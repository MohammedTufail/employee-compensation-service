# Employee Compensation Service (Python)

Azure Functions (HTTP-triggered, Python v2 programming model) backend for
managing Employee/Department records and answering bonus-reporting
questions, backed by Azure SQL / SQL Server via `pyodbc`. All reads and
writes go through the Functions layer — there is no direct database access
from clients.

This is a Python port of the same design used in the TypeScript version of
this project: same schema, same SQL, same error-handling and pooling
philosophy, same Part C decisions — only the language and its idioms differ.

## Tech stack

- **Runtime:** Azure Functions v4, Python 3.9–3.11, v2 programming model (Blueprints)
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

> Note: employee/department shapes are passed around as plain `dict`s
> (matching the JSON wire format) rather than dataclasses, because the
> update payload needs to distinguish "field not sent" from "field sent as
> null" (for clearing a bonus) — Python dicts do this naturally with `in`
> checks, without extra sentinel values.

## Setup & running locally

1. **Prerequisites:**
   - Python 3.9–3.11
   - [Azure Functions Core Tools v4](https://learn.microsoft.com/azure/azure-functions/functions-run-local)
   - The **ODBC Driver 18 for SQL Server** installed on your machine (`pyodbc` talks to SQL Server through it, not directly) — see [Microsoft's install docs](https://learn.microsoft.com/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server) for your OS.
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

| Method | Route | Description |
|---|---|---|
| `POST` | `/api/employees` | Create an employee. Body: `firstName, lastName, departmentId, salary, hireDate` and optional `bonus`. |
| `GET` | `/api/employees/{id}` | Get a single employee by ID. `404` if not found. |
| `GET` | `/api/employees?departmentId={id}` | List employees, optionally filtered by department. |
| `PUT` | `/api/employees/{id}` | Partial update — send only the fields that change. |
| `DELETE` | `/api/employees/{id}` | Delete an employee. Returns `204`. |

### Part B — Compensation reporting

| Method | Route | Description |
|---|---|---|
| `GET` | `/api/reports/total-bonus` | Total bonus paid company-wide (`NULL` treated as 0). Optional `?applyDefaultBonus=true` (see below). |
| `GET` | `/api/reports/employees-without-bonus` | Employees who have never received a bonus. |
| `GET` | `/api/reports/bonus-percentage` | For each employee **with** a bonus, bonus as % of salary, rounded to 2 dp. |
| `GET` | `/api/reports/departments-bonus-exceeds-avg-salary` | Departments where total bonus paid > that department's average salary. |
| `GET` | `/api/reports/employees-ranked-by-bonus` | All employees ranked by bonus, descending; no-bonus employees ranked last (not excluded). |
| `GET` | `/api/reports/highest-salary-employee` | Highest base-salary employee, and whether they also have the highest total compensation. |

All endpoints return JSON and appropriate status codes (`200`, `201`, `204`, `400` for validation errors, `404` for missing resources, `500` for unexpected failures).

## Assumptions and design decisions

(Same as the TypeScript version — the business logic and SQL are identical.)

- **Partial updates.** `PUT /employees/{id}` only changes the fields supplied.
- **Bonus/salary validation.** Salary and bonus must be non-negative; bonus may be explicitly `null` to represent "no bonus."
- **Tie-breaking.** Ties for "highest salary" / "highest total compensation" are broken by the lowest `EmployeeID`. The seed data deliberately makes the highest-salary employee (Ananya Iyer, Finance) **not** the highest-total-comp employee (Simran Kaur, Sales, due to a large bonus), so this report is a real check.
- **Ranking NULLs last.** SQL Server sorts `NULL` first in a `DESC` ordering by default, so the ranking query uses an explicit `CASE` key to force no-bonus employees to the bottom.
- **Departments-vs-bonus report.** "The department's average salary" is the average salary of employees *within that department*.

### Part C — Production readiness

- **No secrets in source.** Connection details come only from environment variables (`SQL_SERVER`, `SQL_DATABASE`, `SQL_USER`, `SQL_PASSWORD`) — see `db/connection.py`. Locally these come from `local.settings.json` (git-ignored); in Azure they'd be Function App Application Settings, ideally as **Key Vault references**, or replaced with Managed Identity + Azure AD auth to Azure SQL for a zero-secrets setup.
- **Error handling.** Every function is wrapped by `with_error_handling` (`utils/http_helpers.py`), which catches a typed `AppError` (validation → `400`, not found → `404`) and reduces anything else to a logged `500`, never leaking internals to the client.
- **Connection pooling.** Unlike Node's `mssql` package, `pyodbc` has no built-in pool, and a single shared connection isn't safe under concurrent invocations. `db/connection.py` implements a small fixed-size pool with a thread-safe `queue.Queue`, handing out a validated connection per request via a context manager (`with get_connection() as conn:`) and returning it afterwards.
- **SQL injection.** All queries use `pyodbc`'s parameterized `?` placeholders — no string concatenation of user input into SQL.
- **Optional: default 5% bonus.** Implemented as computed **at read time**, not written into the `Bonus` column — see the docstring in `repositories/reports_repository.py`. Writing a computed default into the column would permanently destroy the "no bonus recorded" signal that Part B's own reports depend on, and would go stale whenever salary changes. Exposed as an explicit opt-in `?applyDefaultBonus=true` query parameter on `total-bonus`, rather than always-on, so it never silently contradicts the literal Part B definitions.

## What's not included (out of scope / time-boxed)

- Authentication/authorization beyond the Functions `function`-level key.
- Integration tests against a live database (the included tests cover the pure validation logic only).
