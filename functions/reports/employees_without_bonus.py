import azure.functions as func

from repositories.reports_repository import get_employees_without_bonus
from utils.http_helpers import ok, with_error_handling

bp = func.Blueprint()


@bp.route(route="reports/employees-without-bonus", methods=["GET"])
def employees_without_bonus(req: func.HttpRequest) -> func.HttpResponse:
    def handler() -> func.HttpResponse:
        employees = get_employees_without_bonus()
        return ok(employees)

    return with_error_handling(handler)
