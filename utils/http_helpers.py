import json
import logging
from typing import Any, Callable

import azure.functions as func

from utils.errors import AppError


def json_response(status: int, body: Any) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps(body, default=str),
        status_code=status,
        mimetype="application/json",
    )


def ok(body: Any) -> func.HttpResponse:
    return json_response(200, body)


def created(body: Any) -> func.HttpResponse:
    return json_response(201, body)


def no_content() -> func.HttpResponse:
    return func.HttpResponse(status_code=204)


def with_error_handling(fn: Callable[[], func.HttpResponse]) -> func.HttpResponse:
    """
    Wraps a handler body so every function returns a well-formed error
    response instead of an unhandled exception / a raw 500 with a stack
    trace leaking to the client. AppError carries the intended status code
    (400 validation, 404 not found); anything else is logged server-side
    and reduced to a generic 500.
    """
    try:
        return fn()
    except AppError as err:
        return json_response(err.status, {"error": err.message})
    except Exception:  # noqa: BLE001 - deliberate catch-all boundary
        logging.exception("Unhandled error")
        return json_response(500, {"error": "An unexpected error occurred."})
