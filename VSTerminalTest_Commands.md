# Terminal Tests (PowerShell)

Copy-paste commands for testing the API directly from the VS Code
integrated terminal, using `Invoke-RestMethod`. Run these **in order** —
Part A's Create/Get/Update/Delete sequence stores the new employee's ID in
`$employeeId` and reuses it, so you don't have to hardcode or hunt for an ID.

**Start the Function App first, in its own terminal:**

```powershell
func start
```

Then run the commands below in a second terminal.

---

## Part A — Employee CRUD

### 1. Create Employee

```powershell
$body = @{
    firstName    = "Test"
    lastName     = "Employee"
    departmentId = 1
    salary       = 750000
    bonus        = 50000
    hireDate     = "2026-09-07"
} | ConvertTo-Json

$created = Invoke-RestMethod -Uri "http://localhost:7071/api/employees" -Method Post -Body $body -ContentType "application/json"
$created
$employeeId = $created.employeeId
```

Expected: the created employee is printed, with a `201 Created` behind the
scenes. `$employeeId` now holds the new row's ID for the rest of this
session.

### 2. Get Employee

```powershell
Invoke-RestMethod "http://localhost:7071/api/employees/$employeeId"
```

### 3. Get All Employees

```powershell
Invoke-RestMethod "http://localhost:7071/api/employees" | Format-Table
```

### 4. Filter Employees by Department

```powershell
Invoke-RestMethod "http://localhost:7071/api/employees?departmentId=2"
```

You should get: Simran Kaur, Arjun Rao, Neha Joshi.

### 5. Update Employee Bonus

```powershell
$body = @{ bonus = 100000 } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:7071/api/employees/$employeeId" -Method Put -Body $body -ContentType "application/json"
```

### 6. Test Partial Update

```powershell
$body = @{ salary = 800000 } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:7071/api/employees/$employeeId" -Method Put -Body $body -ContentType "application/json"
```

Only `salary` should change — check the output against the previous step.

### 7. Set Bonus to NULL

```powershell
$body = @{ bonus = $null } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:7071/api/employees/$employeeId" -Method Put -Body $body -ContentType "application/json"
```

The response should show `bonus` as empty/null.

### 8. Delete Employee

```powershell
Invoke-RestMethod -Uri "http://localhost:7071/api/employees/$employeeId" -Method Delete
```

No output on success (`204 No Content`).

### 9. Verify Delete

```powershell
try {
    Invoke-RestMethod "http://localhost:7071/api/employees/$employeeId"
} catch {
    $_.Exception.Response.StatusCode.value__
}
```

Expected: `404`

---

## Part B — Compensation Reports

### 10. Total Bonus

```powershell
Invoke-RestMethod "http://localhost:7071/api/reports/total-bonus"
```

Expected total from seed data: `1990000`, `applyDefaultBonus: False`.

### 11. Employees Without Bonus

```powershell
Invoke-RestMethod "http://localhost:7071/api/reports/employees-without-bonus" | Format-Table
```

Expected: Rohan Mehta, Karan Verma, Neha Joshi, Vikram Desai, Meera Pillai
— all with a null bonus.

### 12. Bonus Percentage

```powershell
Invoke-RestMethod "http://localhost:7071/api/reports/bonus-percentage" | ConvertTo-Json -Depth 10
```

Employees with a `NULL` bonus should not appear. Example: Simran Kaur →
128.57%.

### 13. Departments Where Bonus Exceeds Average Salary

```powershell
Invoke-RestMethod "http://localhost:7071/api/reports/departments-bonus-exceeds-avg-salary" | ConvertTo-Json -Depth 10
```

Based on the seed data, Sales should qualify:

```
Sales bonus         = 900,000 + 480,000 = 1,380,000
Sales average salary = (700,000 + 650,000 + 600,000) / 3 = 650,000
1,380,000 > 650,000  →  Sales qualifies
```

### 14. Employees Ranked by Bonus

```powershell
Invoke-RestMethod "http://localhost:7071/api/reports/employees-ranked-by-bonus" | ConvertTo-Json -Depth 10
```

The first employee should be Simran Kaur → 900,000, with `NULL`-bonus
employees appearing at the bottom of the list.

### 15. Highest Salary vs. Total Compensation

```powershell
Invoke-RestMethod "http://localhost:7071/api/reports/highest-salary-employee" | ConvertTo-Json -Depth 10
```

Expected:

```
Highest Salary:              Ananya Iyer, 1,300,000
Highest Total Compensation:  Simran Kaur, 1,600,000
alsoHasHighestTotalCompensation: false
```

### 20. Default 5% Bonus (optional Part C feature)

```powershell
Invoke-RestMethod "http://localhost:7071/api/reports/total-bonus?applyDefaultBonus=true"
```

This should produce a larger total than test 10, because employees whose
`Bonus` is `NULL` are temporarily treated as receiving the configured 5%
default bonus **for this response only** — the stored values are unchanged.
Confirm that by re-running test 10 afterwards and checking the total is
back to `1990000`.

---

## Part C — Error Tests

`Invoke-RestMethod` throws on non-2xx responses, so these use `try/catch`
to surface the status code and error body instead of just failing.

### 16. Employee Not Found

```powershell
try {
    Invoke-RestMethod "http://localhost:7071/api/employees/99999"
} catch {
    $_.Exception.Response.StatusCode.value__
    $_.ErrorDetails.Message
}
```

Expected: `404`

### 17. Invalid Department

```powershell
$body = @{
    firstName    = "Invalid"
    lastName     = "Department"
    departmentId = 9999
    salary       = 500000
    bonus        = 50000
    hireDate     = "2026-09-07"
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "http://localhost:7071/api/employees" -Method Post -Body $body -ContentType "application/json"
} catch {
    $_.Exception.Response.StatusCode.value__
    $_.ErrorDetails.Message
}
```

Expected: `400`

### 18. Negative Salary

```powershell
$body = @{
    firstName    = "Invalid"
    lastName     = "Salary"
    departmentId = 1
    salary       = -500000
    bonus        = 50000
    hireDate     = "2026-09-07"
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "http://localhost:7071/api/employees" -Method Post -Body $body -ContentType "application/json"
} catch {
    $_.Exception.Response.StatusCode.value__
    $_.ErrorDetails.Message
}
```

Expected: `400`

### 19. Negative Bonus

```powershell
$body = @{
    firstName    = "Invalid"
    lastName     = "Bonus"
    departmentId = 1
    salary       = 500000
    bonus        = -10000
    hireDate     = "2026-09-07"
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "http://localhost:7071/api/employees" -Method Post -Body $body -ContentType "application/json"
} catch {
    $_.Exception.Response.StatusCode.value__
    $_.ErrorDetails.Message
}
```

Expected: `400`

---

## Quick full run

If you just want to blast through Part B in one go once the app is
running (no Part A dependency, since it only reads):

```powershell
Invoke-RestMethod "http://localhost:7071/api/reports/total-bonus"
Invoke-RestMethod "http://localhost:7071/api/reports/employees-without-bonus"
Invoke-RestMethod "http://localhost:7071/api/reports/bonus-percentage" | ConvertTo-Json -Depth 10
Invoke-RestMethod "http://localhost:7071/api/reports/departments-bonus-exceeds-avg-salary" | ConvertTo-Json -Depth 10
Invoke-RestMethod "http://localhost:7071/api/reports/employees-ranked-by-bonus" | ConvertTo-Json -Depth 10
Invoke-RestMethod "http://localhost:7071/api/reports/highest-salary-employee" | ConvertTo-Json -Depth 10
Invoke-RestMethod "http://localhost:7071/api/reports/total-bonus?applyDefaultBonus=true"
```