Thunder Client API Tests
Base URL
http://localhost:7071/api

Start the Function App first:

func start

Part A — Employee CRUD

1. Create Employee

POST

http://localhost:7071/api/employees

Body → JSON
{
"firstName": "Test",
"lastName": "Employee",
"departmentId": 1,
"salary": 750000,
"bonus": 50000,
"hireDate": "2026-09-07"
}

Expected: 201 Created

2. Get Employee

GET

http://localhost:7071/api/employees/14

Expected: 200 OK

Use the employeeId returned by the Create request if it is different from 14.

3. Get All Employees

GET

http://localhost:7071/api/employees

Expected: 200 OK

4. Filter Employees by Department

GET

http://localhost:7071/api/employees?departmentId=1

Expected: 200 OK

All returned employees should have departmentId: 1.

5. Update Employee Bonus

PUT

http://localhost:7071/api/employees/14

Body → JSON
{
"bonus": 100000
}

Expected: 200 OK

6. Test Partial Update

PUT

http://localhost:7071/api/employees/14

Body → JSON
{
"salary": 800000
}

Expected: 200 OK

Only the salary should change. Other fields should remain unchanged.

7. Set Bonus to NULL

PUT

http://localhost:7071/api/employees/14

Body → JSON
{
"bonus": null
}

Expected: 200 OK

The response should contain:

"bonus": null

8. Delete Employee

DELETE

http://localhost:7071/api/employees/14

Expected: 204 No Content

9. Verify Delete

GET

http://localhost:7071/api/employees/14

Expected: 404 Not Found

Part B — Compensation Reports 10. Total Bonus

GET

http://localhost:7071/api/reports/total-bonus

Expected: 200 OK

Expected total from seed data:

1990000

11. Employees Without Bonus

GET

http://localhost:7071/api/reports/employees-without-bonus

Expected: 200 OK

Expected employees include:

Rohan Mehta
Karan Verma
Neha Joshi
Vikram Desai
Meera Pillai

Their bonus should be null.

12. Bonus Percentage

GET

http://localhost:7071/api/reports/bonus-percentage

Expected: 200 OK

Employees with NULL bonus should not appear.

Example:

Simran Kaur → 128.57%

13. Departments Where Bonus Exceeds Average Salary

GET

http://localhost:7071/api/reports/departments-bonus-exceeds-avg-salary

Expected: 200 OK

Expected department:

Sales

14. Employees Ranked by Bonus

GET

http://localhost:7071/api/reports/employees-ranked-by-bonus

Expected: 200 OK

Expected ranking starts approximately:

1. Simran Kaur 900000
2. Arjun Rao 480000
3. Ananya Iyer 200000
4. Aditi Sharma 150000
5. Siddharth Kapoor 150000
6. Priya Nair 90000
7. Fatima Sheikh 20000

Employees with NULL bonus should appear last.

15. Highest Salary vs Total Compensation

GET

http://localhost:7071/api/reports/highest-salary-employee

Expected: 200 OK

Expected result:

Highest Salary:
Ananya Iyer
Salary: 1300000

Highest Total Compensation:
Simran Kaur
Total Compensation: 1600000

alsoHasHighestTotalCompensation:
false

Part C — Error Tests 16. Employee Not Found

GET

http://localhost:7071/api/employees/99999

Expected: 404 Not Found

17. Invalid Department

POST

http://localhost:7071/api/employees

Body → JSON
{
"firstName": "Invalid",
"lastName": "Department",
"departmentId": 9999,
"salary": 500000,
"bonus": 50000,
"hireDate": "2026-09-07"
}

Expected: 400 Bad Request

18. Negative Salary

POST

http://localhost:7071/api/employees

Body → JSON
{
"firstName": "Invalid",
"lastName": "Salary",
"departmentId": 1,
"salary": -500000,
"bonus": 50000,
"hireDate": "2026-09-07"
}

Expected: 400 Bad Request

19. Negative Bonus

POST

http://localhost:7071/api/employees

Body → JSON
{
"firstName": "Invalid",
"lastName": "Bonus",
"departmentId": 1,
"salary": 500000,
"bonus": -10000,
"hireDate": "2026-09-07"
}

Expected: 400 Bad Request

Optional Default Bonus Test 20. Total Bonus With 5% Default

GET

http://localhost:7071/api/reports/total-bonus?applyDefaultBonus=true

Expected: 200 OK

Employees with NULL bonus should have a calculated bonus of 5% of salary for this calculation.

The database values should remain unchanged.
