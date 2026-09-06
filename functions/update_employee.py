import azure.functions as func

from repositories.employee_repository import update_employee as update_employee_repo
from utils.errors import AppError
from utils.http_helpers import ok, with_error_handling
from utils.validation import parse_id_param, validate_update_employee

bp = func.Blueprint()


@bp.route(route="employees/{id}", methods=["PUT"])
def update_employee(req: func.HttpRequest) -> func.HttpResponse:
    def handler() -> func.HttpResponse:
        employee_id = parse_id_param(req.route_params.get("id"))
        try:
            body = req.get_json()
        except ValueError:
            raise AppError(400, "Request body must be valid JSON.") from None
        update = validate_update_employee(body)
        employee = update_employee_repo(employee_id, update)
        if employee is None:
            raise AppError(404, f"Employee {employee_id} was not found.")
        return ok(employee)

    return with_error_handling(handler)
