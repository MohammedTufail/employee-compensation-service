import azure.functions as func

from repositories.employee_repository import create_employee as create_employee_repo
from utils.errors import AppError
from utils.http_helpers import created, with_error_handling
from utils.validation import validate_create_employee

bp = func.Blueprint()


@bp.route(route="employees", methods=["POST"])
def create_employee(req: func.HttpRequest) -> func.HttpResponse:
    def handler() -> func.HttpResponse:
        try:
            body = req.get_json()
        except ValueError:
            raise AppError(400, "Request body must be valid JSON.") from None
        data = validate_create_employee(body)
        employee = create_employee_repo(data)
        return created(employee)

    return with_error_handling(handler)
