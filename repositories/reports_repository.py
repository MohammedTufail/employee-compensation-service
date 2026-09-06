import os
from typing import Any, Dict, List

from db.connection import get_connection


def _default_bonus_rate() -> float:
    raw = os.environ.get("DEFAULT_BONUS_RATE", "0.05")
    try:
        return float(raw)
    except ValueError:
        return 0.05


# 1. Total bonus paid across the whole company (NULL treated as 0, or as the
#    default 5% projection when requested).
def get_total_bonus_paid(apply_default_bonus: bool = False) -> float:
    with get_connection() as conn:
        cursor = conn.cursor()
        if apply_default_bonus:
            cursor.execute(
                "SELECT SUM(ISNULL(Bonus, Salary * ?)) AS TotalBonus FROM Employee",
                _default_bonus_rate(),
            )
        else:
            cursor.execute("SELECT SUM(ISNULL(Bonus, 0)) AS TotalBonus FROM Employee")
        row = cursor.fetchone()
        return float(row.TotalBonus or 0)


# 2. Employees who have never received a bonus (raw persisted state -
#    always ignores the default-bonus projection; see module docstring).
def get_employees_without_bonus() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Employee WHERE Bonus IS NULL ORDER BY EmployeeID")
        return [
            {
                "employeeId": r.EmployeeID,
                "firstName": r.FirstName,
                "lastName": r.LastName,
                "departmentId": r.DepartmentID,
                "salary": float(r.Salary),
                "bonus": None,
                "hireDate": r.HireDate.isoformat() if r.HireDate else None,
            }
            for r in cursor.fetchall()
        ]


# 3. For each employee who HAS a bonus, bonus as a % of salary (2 dp).
def get_bonus_percentages() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                EmployeeID, FirstName, LastName, Salary, Bonus,
                ROUND((Bonus / Salary) * 100.0, 2) AS BonusPercentage
            FROM Employee
            WHERE Bonus IS NOT NULL
            ORDER BY BonusPercentage DESC
            """
        )
        return [
            {
                "employeeId": r.EmployeeID,
                "firstName": r.FirstName,
                "lastName": r.LastName,
                "salary": float(r.Salary),
                "bonus": float(r.Bonus),
                "bonusPercentage": float(r.BonusPercentage),
            }
            for r in cursor.fetchall()
        ]


# 4. Departments where total bonus paid exceeds the department's average
#    salary.
def get_departments_where_bonus_exceeds_avg_salary() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                d.DepartmentID, d.DepartmentName,
                SUM(ISNULL(e.Bonus, 0)) AS TotalBonusPaid,
                AVG(e.Salary) AS AverageSalary
            FROM Department d
            JOIN Employee e ON e.DepartmentID = d.DepartmentID
            GROUP BY d.DepartmentID, d.DepartmentName
            HAVING SUM(ISNULL(e.Bonus, 0)) > AVG(e.Salary)
            ORDER BY d.DepartmentID
            """
        )
        return [
            {
                "departmentId": r.DepartmentID,
                "departmentName": r.DepartmentName,
                "totalBonusPaid": float(r.TotalBonusPaid),
                "averageSalary": float(r.AverageSalary),
            }
            for r in cursor.fetchall()
        ]


# 5. Employees ranked by bonus amount, descending; employees with no bonus
#    ranked last rather than excluded (NULLs sort first in a DESC order in
#    SQL Server by default, so this is forced explicitly with a CASE key).
def get_employees_ranked_by_bonus() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                EmployeeID, FirstName, LastName, Bonus,
                RANK() OVER (
                    ORDER BY CASE WHEN Bonus IS NULL THEN 1 ELSE 0 END, Bonus DESC
                ) AS BonusRank
            FROM Employee
            ORDER BY BonusRank
            """
        )
        return [
            {
                "rank": r.BonusRank,
                "employeeId": r.EmployeeID,
                "firstName": r.FirstName,
                "lastName": r.LastName,
                "bonus": float(r.Bonus) if r.Bonus is not None else None,
            }
            for r in cursor.fetchall()
        ]


# 6. Highest base-salary employee, and whether that same person also has the
#    highest total compensation (salary + bonus).
#    Assumption: ties are broken by the lowest EmployeeID so the result is
#    deterministic.
def get_highest_salary_vs_highest_total_comp() -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT TOP 1 EmployeeID, FirstName, LastName, Salary, Bonus
            FROM Employee
            ORDER BY Salary DESC, EmployeeID ASC
            """
        )
        s = cursor.fetchone()

        cursor.execute(
            """
            SELECT TOP 1 EmployeeID, FirstName, LastName,
                   (Salary + ISNULL(Bonus, 0)) AS TotalCompensation
            FROM Employee
            ORDER BY (Salary + ISNULL(Bonus, 0)) DESC, EmployeeID ASC
            """
        )
        t = cursor.fetchone()

        return {
            "highestSalaryEmployee": {
                "employeeId": s.EmployeeID,
                "firstName": s.FirstName,
                "lastName": s.LastName,
                "salary": float(s.Salary),
                "bonus": float(s.Bonus) if s.Bonus is not None else None,
            },
            "alsoHasHighestTotalCompensation": s.EmployeeID == t.EmployeeID,
            "highestTotalCompensationEmployee": {
                "employeeId": t.EmployeeID,
                "firstName": t.FirstName,
                "lastName": t.LastName,
                "totalCompensation": float(t.TotalCompensation),
            },
        }
