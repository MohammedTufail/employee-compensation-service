import re
from typing import Any, Dict, Optional

from utils.errors import AppError

DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _is_non_empty_str(v: Any) -> bool:
    return isinstance(v, str) and v.strip() != ""


def _is_number(v: Any) -> bool:
    # bool is a subclass of int in Python - explicitly exclude it so
    # {"salary": true} doesn't sneak past as a number.
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def validate_create_employee(body: Any) -> Dict[str, Any]:
    if not isinstance(body, dict):
        raise AppError(400, "Request body must be a JSON object.")

    if not _is_non_empty_str(body.get("firstName")):
        raise AppError(400, "firstName is required and must be a non-empty string.")
    if not _is_non_empty_str(body.get("lastName")):
        raise AppError(400, "lastName is required and must be a non-empty string.")
    if not _is_number(body.get("departmentId")):
        raise AppError(400, "departmentId is required and must be a number.")

    salary = body.get("salary")
    if not _is_number(salary) or salary < 0:
        raise AppError(400, "salary is required and must be a non-negative number.")

    bonus = body.get("bonus")
    if bonus is not None and (not _is_number(bonus) or bonus < 0):
        raise AppError(400, "bonus, if provided, must be a non-negative number.")

    hire_date = body.get("hireDate")
    if not _is_non_empty_str(hire_date) or not DATE_REGEX.match(hire_date):
        raise AppError(400, "hireDate is required and must be in YYYY-MM-DD format.")

    return {
        "first_name": body["firstName"].strip(),
        "last_name": body["lastName"].strip(),
        "department_id": int(body["departmentId"]),
        "salary": float(salary),
        "bonus": float(bonus) if bonus is not None else None,
        "hire_date": hire_date,
    }


def validate_update_employee(body: Any) -> Dict[str, Any]:
    if not isinstance(body, dict):
        raise AppError(400, "Request body must be a JSON object.")

    update: Dict[str, Any] = {}

    if "firstName" in body:
        if not _is_non_empty_str(body["firstName"]):
            raise AppError(400, "firstName must be a non-empty string.")
        update["first_name"] = body["firstName"].strip()

    if "lastName" in body:
        if not _is_non_empty_str(body["lastName"]):
            raise AppError(400, "lastName must be a non-empty string.")
        update["last_name"] = body["lastName"].strip()

    if "departmentId" in body:
        if not _is_number(body["departmentId"]):
            raise AppError(400, "departmentId must be a number.")
        update["department_id"] = int(body["departmentId"])

    if "salary" in body:
        salary = body["salary"]
        if not _is_number(salary) or salary < 0:
            raise AppError(400, "salary must be a non-negative number.")
        update["salary"] = float(salary)

    if "bonus" in body:
        bonus = body["bonus"]
        if bonus is not None and (not _is_number(bonus) or bonus < 0):
            raise AppError(400, "bonus must be a non-negative number or null.")
        update["bonus"] = float(bonus) if bonus is not None else None

    if "hireDate" in body:
        hire_date = body["hireDate"]
        if not _is_non_empty_str(hire_date) or not DATE_REGEX.match(hire_date):
            raise AppError(400, "hireDate must be in YYYY-MM-DD format.")
        update["hire_date"] = hire_date

    if not update:
        raise AppError(400, "Request body must contain at least one field to update.")

    return update


def parse_id_param(raw: Optional[str]) -> int:
    if raw is None:
        raise AppError(400, "id must be a positive integer.")
    try:
        value = int(raw)
    except ValueError:
        raise AppError(400, "id must be a positive integer.") from None
    if value <= 0:
        raise AppError(400, "id must be a positive integer.")
    return value
