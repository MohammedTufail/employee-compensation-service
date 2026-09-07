# API Testing Reference

Manual test plan for the Employee Compensation Service, covering Part A
(CRUD), Part B (compensation reports), and Part C (error handling).

Tested with [Thunder Client](https://www.thunderclient.com/) (VS Code
extension), but every request below also has an equivalent PowerShell
one-liner in [`TERMINAL-TESTS.md`](./TERMINAL-TESTS.md) if you'd rather run
everything from the integrated terminal.

## Prerequisites

Start the Function App first:

```bash
func start
```

**Base URL:** `http://localhost:7071/api`

---

## Part A — Employee CRUD

### 1. Create Employee

`POST /employees`

```json
{
  "firstName": "Test",
  "lastName": "Employee",
  "departmentId": 1,
  "salary": 750000,
  "bonus": 50000,
  "hireDate": "2026-09-07"
}
```

**Expected:** `201 Created`

> Note the `employeeId` returned in the response — you'll need it for tests 2, 5–9.

### 2. Get Employee

`GET /employees/{id}`

Use the `employeeId` from test 1 (the examples below use `14` as a
placeholder — substitute your own).

```
GET http://localhost:7071/api/employees/14
```

**Expected:** `200 OK`

### 3. Get All Employees

```
GET http://localhost:7071/api/employees
```

**Expected:** `200 OK`

### 4. Filter Employees by Department

```
GET http://localhost:7071/api/employees?departmentId=1
```

**Expected:** `200 OK` — every returned employee has `departmentId: 1`.

### 5. Update Employee Bonus

`PUT /employees/{id}`

```json
{ "bonus": 100000 }
```

**Expected:** `200 OK`

### 6. Test Partial Update

`PUT /employees/{id}`

```json
{ "salary": 800000 }
```

**Expected:** `200 OK` — only `salary` changes; every other field is untouched.

### 7. Set Bonus to NULL

`PUT /employees/{id}`

```json
{ "bonus": null }
```

**Expected:** `200 OK`, response contains `"bonus": null`.

### 8. Delete Employee

```
DELETE http://localhost:7071/api/employees/14
```

**Expected:** `204 No Content`

### 9. Verify Delete

```
GET http://localhost:7071/api/employees/14
```

**Expected:** `404 Not Found`

---

## Part B — Compensation Reports

### 10. Total Bonus

```
GET http://localhost:7071/api/reports/total-bonus
```

**Expected:** `200 OK` — total from seed data: **1,990,000**

### 11. Employees Without Bonus

```
GET http://localhost:7071/api/reports/employees-without-bonus
```

**Expected:** `200 OK` — includes Rohan Mehta, Karan Verma, Neha Joshi,
Vikram Desai, Meera Pillai, each with `"bonus": null`.

### 12. Bonus Percentage

```
GET http://localhost:7071/api/reports/bonus-percentage
```

**Expected:** `200 OK` — employees with a `NULL` bonus are excluded.
Example: **Simran Kaur → 128.57%**

### 13. Departments Where Bonus Exceeds Average Salary

```
GET http://localhost:7071/api/reports/departments-bonus-exceeds-avg-salary
```

**Expected:** `200 OK` — includes **Sales**.

### 14. Employees Ranked by Bonus

```
GET http://localhost:7071/api/reports/employees-ranked-by-bonus
```

**Expected:** `200 OK`, ranking starting approximately:

| Rank | Employee | Bonus |
|---|---|---|
| 1 | Simran Kaur | 900,000 |
| 2 | Arjun Rao | 480,000 |
| 3 | Ananya Iyer | 200,000 |
| 4 | Aditi Sharma | 150,000 |
| 5 | Siddharth Kapoor | 150,000 |
| 6 | Priya Nair | 90,000 |
| 7 | Fatima Sheikh | 20,000 |

Employees with a `NULL` bonus appear last.

### 15. Highest Salary vs. Total Compensation

```
GET http://localhost:7071/api/reports/highest-salary-employee
```

**Expected:** `200 OK`

- **Highest salary:** Ananya Iyer — 1,300,000
- **Highest total compensation:** Simran Kaur — 1,600,000
- **`alsoHasHighestTotalCompensation`:** `false`

---

## Part C — Error Tests

### 16. Employee Not Found

```
GET http://localhost:7071/api/employees/99999
```

**Expected:** `404 Not Found`

### 17. Invalid Department

`POST /employees`

```json
{
  "firstName": "Invalid",
  "lastName": "Department",
  "departmentId": 9999,
  "salary": 500000,
  "bonus": 50000,
  "hireDate": "2026-09-07"
}
```

**Expected:** `400 Bad Request`

### 18. Negative Salary

`POST /employees`

```json
{
  "firstName": "Invalid",
  "lastName": "Salary",
  "departmentId": 1,
  "salary": -500000,
  "bonus": 50000,
  "hireDate": "2026-09-07"
}
```

**Expected:** `400 Bad Request`

### 19. Negative Bonus

`POST /employees`

```json
{
  "firstName": "Invalid",
  "lastName": "Bonus",
  "departmentId": 1,
  "salary": 500000,
  "bonus": -10000,
  "hireDate": "2026-09-07"
}
```

**Expected:** `400 Bad Request`

---

## Optional — Default Bonus Test

### 20. Total Bonus With 5% Default

```
GET http://localhost:7071/api/reports/total-bonus?applyDefaultBonus=true
```

**Expected:** `200 OK` — employees with a `NULL` bonus are treated as
receiving 5% of their salary **for this calculation only**. The underlying
database values are never modified.