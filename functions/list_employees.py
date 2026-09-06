import azure.functions as func

from repositories.employee_repository import list_employees as list_employees_repo
from utils.errors import AppError
from utils.http_helpers import ok, with_error_handling

bp = func.Blueprint()


@bp.route(route="employees", methods=["GET"])
def list_employees(req: func.HttpRequest) -> func.HttpResponse:
    def handler() -> func.HttpResponse:
        raw = req.params.get("departmentId")
        department_id = None
        if raw:
            try:
                department_id = int(raw)
            except ValueError:
                raise AppError(
                    400, "departmentId query parameter must be a positive integer."
                ) from None
            if department_id <= 0:
                raise AppError(400, "departmentId query parameter must be a positive integer.")
        employees = list_employees_repo(department_id)
        return ok(employees)

    return with_error_handling(handler)
