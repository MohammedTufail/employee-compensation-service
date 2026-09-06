import azure.functions as func

from repositories.reports_repository import get_total_bonus_paid
from utils.http_helpers import ok, with_error_handling

bp = func.Blueprint()


@bp.route(route="reports/total-bonus", methods=["GET"])
def total_bonus(req: func.HttpRequest) -> func.HttpResponse:
    def handler() -> func.HttpResponse:
        apply_default_bonus = req.params.get("applyDefaultBonus") == "true"
        total_bonus_paid = get_total_bonus_paid(apply_default_bonus)
        return ok({"totalBonusPaid": total_bonus_paid, "applyDefaultBonus": apply_default_bonus})

    return with_error_handling(handler)
