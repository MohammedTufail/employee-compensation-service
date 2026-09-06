import azure.functions as func

from repositories.reports_repository import get_employees_ranked_by_bonus
from utils.http_helpers import ok, with_error_handling

bp = func.Blueprint()


@bp.route(route="reports/employees-ranked-by-bonus", methods=["GET"])
def employees_ranked_by_bonus(req: func.HttpRequest) -> func.HttpResponse:
    def handler() -> func.HttpResponse:
        rows = get_employees_ranked_by_bonus()
        return ok(rows)

    return with_error_handling(handler)
