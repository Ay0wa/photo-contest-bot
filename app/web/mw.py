import json
import typing

from aiohttp.web_exceptions import (
    HTTPConflict,
    HTTPException,
    HTTPNotFound,
    HTTPUnprocessableEntity,
)
from aiohttp.web_middlewares import middleware
from aiohttp_apispec import validation_middleware
from aiohttp_session import get_session

from app.web.utils import error_json_response

if typing.TYPE_CHECKING:
    from app.web.app import Application, Request

HTTP_ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "not_implemented",
    409: "conflict",
    500: "internal_server_error",
}


@middleware
async def auth_middleware(request: "Request", handler):
    session = await get_session(request)
    if session and "admin" in session and "email" in session["admin"]:
        email = session["admin"]["email"]
        request.admin = await request.app.store.admins.get_by_email(email)
    else:
        request.admin = None

    return await handler(request)


@middleware
async def error_handling_middleware(request: "Request", handler):
    try:
        response = await handler(request)
    except HTTPUnprocessableEntity as e:
        return error_json_response(
            http_status=400,
            status=HTTP_ERROR_CODES[400],
            message=e.reason,
            data=json.loads(e.text),
        )
    except HTTPException as e:
        return error_json_response(
            http_status=e.status,
            status=HTTP_ERROR_CODES.get(e.status, "unknown_error"),
            message=str(e),
        )
    except HTTPNotFound as e:
        return error_json_response(
            http_status=404,
            status=HTTP_ERROR_CODES[404],
            message=str(e),
        )
    except HTTPConflict as e:
        return error_json_response(
            http_status=409,
            status=HTTP_ERROR_CODES[409],
            message=str(e),
        )
    except Exception as e:
        request.app.logger.error("Unhandled Exception", exc_info=e)
        return error_json_response(
            http_status=500,
            status=HTTP_ERROR_CODES[500],
            message="Internal server error",
        )

    return response


def setup_middlewares(app: "Application"):
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(validation_middleware)
    app.middlewares.append(auth_middleware)
