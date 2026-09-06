import azure.functions as func

from repositories.reports_repository import get_highest_salary_vs_highest_total_comp
from utils.http_helpers import ok, with_error_handling

bp = func.Blueprint()


@bp.route(route="reports/highest-salary-employee", methods=["GET"])
def highest_salary_employee(req: func.HttpRequest) -> func.HttpResponse:
    def handler() -> func.HttpResponse:
        result = get_highest_salary_vs_highest_total_comp()
        return ok(result)

    return with_error_handling(handler)
