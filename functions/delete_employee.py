import azure.functions as func

from repositories.employee_repository import delete_employee as delete_employee_repo
from utils.errors import AppError
from utils.http_helpers import no_content, with_error_handling
from utils.validation import parse_id_param

bp = func.Blueprint()


@bp.route(route="employees/{id}", methods=["DELETE"])
def delete_employee(req: func.HttpRequest) -> func.HttpResponse:
    def handler() -> func.HttpResponse:
        employee_id = parse_id_param(req.route_params.get("id"))
        was_deleted = delete_employee_repo(employee_id)
        if not was_deleted:
            raise AppError(404, f"Employee {employee_id} was not found.")
        return no_content()

    return with_error_handling(handler)
