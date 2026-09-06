import azure.functions as func

from repositories.reports_repository import get_departments_where_bonus_exceeds_avg_salary
from utils.http_helpers import ok, with_error_handling

bp = func.Blueprint()


@bp.route(route="reports/departments-bonus-exceeds-avg-salary", methods=["GET"])
def departments_bonus_exceeds_avg_salary(req: func.HttpRequest) -> func.HttpResponse:
    def handler() -> func.HttpResponse:
        rows = get_departments_where_bonus_exceeds_avg_salary()
        return ok(rows)

    return with_error_handling(handler)
