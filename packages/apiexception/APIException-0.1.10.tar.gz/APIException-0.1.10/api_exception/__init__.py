from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .logger import logger
from .exception import APIException, set_default_http_codes
from custom_enum.enums import ExceptionCode, ExceptionStatus, BaseExceptionCode
from schemas.response_model import ResponseModel

__all__ = [
    "APIException",
    "ExceptionCode",
    "BaseExceptionCode",
    "ExceptionStatus",
    "ResponseModel",
    "register_exception_handlers",
    "set_default_http_codes",
    "logger"
]


def register_exception_handlers(app: FastAPI, use_response_model: bool = True):
    """
    Registers the APIException handler.

    Parameters:
    -----------
    app : FastAPI
        The FastAPI app or sub-app.
    use_response_model : bool, optional
        If True, uses ResponseModel (Pydantic) for responses.
        If False, uses raw dict format.
    """

    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        logger.error(f"Exception handled for path: {request.url.path}")
        if use_response_model:
            content = exc.to_response_model().model_dump()
        else:
            content = exc.to_response()
        return JSONResponse(
            status_code=exc.http_status_code,
            content=content
        )
