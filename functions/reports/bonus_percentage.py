import azure.functions as func

from repositories.reports_repository import get_bonus_percentages
from utils.http_helpers import ok, with_error_handling

bp = func.Blueprint()


@bp.route(route="reports/bonus-percentage", methods=["GET"])
def bonus_percentage(req: func.HttpRequest) -> func.HttpResponse:
    def handler() -> func.HttpResponse:
        rows = get_bonus_percentages()
        return ok(rows)

    return with_error_handling(handler)
