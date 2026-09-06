from typing import Any, Dict, List, Optional

from db.connection import get_connection
from utils.errors import AppError


def _row_to_employee(row: Any) -> Dict[str, Any]:
    return {
        "employeeId": row.EmployeeID,
        "firstName": row.FirstName,
        "lastName": row.LastName,
        "departmentId": row.DepartmentID,
        "salary": float(row.Salary),
        "bonus": float(row.Bonus) if row.Bonus is not None else None,
        "hireDate": row.HireDate.isoformat() if row.HireDate else None,
    }


def create_employee(data: Dict[str, Any]) -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()

        # Guard against a bad DepartmentID producing a confusing 500 from the
        # FK constraint - surface a clean 400 instead.
        cursor.execute("SELECT 1 FROM Department WHERE DepartmentID = ?", data["department_id"])
        if cursor.fetchone() is None:
            raise AppError(400, f"DepartmentID {data['department_id']} does not exist.")

        cursor.execute(
            """
            INSERT INTO Employee (FirstName, LastName, DepartmentID, Salary, Bonus, HireDate)
            OUTPUT INSERTED.*
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            data["first_name"],
            data["last_name"],
            data["department_id"],
            data["salary"],
            data["bonus"],
            data["hire_date"],
        )
        row = cursor.fetchone()
        return _row_to_employee(row)


def get_employee_by_id(employee_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Employee WHERE EmployeeID = ?", employee_id)
        row = cursor.fetchone()
        return _row_to_employee(row) if row is not None else None


def list_employees(department_id: Optional[int] = None) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        if department_id is not None:
            cursor.execute(
                "SELECT * FROM Employee WHERE DepartmentID = ? ORDER BY EmployeeID",
                department_id,
            )
        else:
            cursor.execute("SELECT * FROM Employee ORDER BY EmployeeID")
        return [_row_to_employee(row) for row in cursor.fetchall()]


def update_employee(employee_id: int, update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Employee WHERE EmployeeID = ?", employee_id)
        existing_row = cursor.fetchone()
        if existing_row is None:
            return None
        existing = _row_to_employee(existing_row)

        if "department_id" in update:
            cursor.execute(
                "SELECT 1 FROM Department WHERE DepartmentID = ?", update["department_id"]
            )
            if cursor.fetchone() is None:
                raise AppError(400, f"DepartmentID {update['department_id']} does not exist.")

        merged_first_name = update.get("first_name", existing["firstName"])
        merged_last_name = update.get("last_name", existing["lastName"])
        merged_department_id = update.get("department_id", existing["departmentId"])
        merged_salary = update.get("salary", existing["salary"])
        merged_bonus = update["bonus"] if "bonus" in update else existing["bonus"]
        merged_hire_date = update.get("hire_date", existing["hireDate"])

        cursor.execute(
            """
            UPDATE Employee
            SET FirstName = ?, LastName = ?, DepartmentID = ?, Salary = ?, Bonus = ?, HireDate = ?
            OUTPUT INSERTED.*
            WHERE EmployeeID = ?
            """,
            merged_first_name,
            merged_last_name,
            merged_department_id,
            merged_salary,
            merged_bonus,
            merged_hire_date,
            employee_id,
        )
        row = cursor.fetchone()
        return _row_to_employee(row)


def delete_employee(employee_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Employee WHERE EmployeeID = ?", employee_id)
        return cursor.rowcount > 0
