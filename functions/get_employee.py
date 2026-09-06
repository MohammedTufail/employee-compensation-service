import azure.functions as func

from repositories.employee_repository import get_employee_by_id
from utils.errors import AppError
from utils.http_helpers import ok, with_error_handling
from utils.validation import parse_id_param

bp = func.Blueprint()


@bp.route(route="employees/{id}", methods=["GET"])
def get_employee(req: func.HttpRequest) -> func.HttpResponse:
    def handler() -> func.HttpResponse:
        employee_id = parse_id_param(req.route_params.get("id"))
        employee = get_employee_by_id(employee_id)
        if employee is None:
            raise AppError(404, f"Employee {employee_id} was not found.")
        return ok(employee)

    return with_error_handling(handler)
