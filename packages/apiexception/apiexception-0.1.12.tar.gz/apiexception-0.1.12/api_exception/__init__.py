from typing import Callable

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from .logger import logger
from .exception import APIException, set_default_http_codes, DEFAULT_HTTP_CODES
from custom_enum.enums import ExceptionCode, ExceptionStatus, BaseExceptionCode
from schemas.response_model import ResponseModel
from .response_utils import APIResponse
import traceback


__all__ = [
    "DEFAULT_HTTP_CODES",
    "APIException",
    "ExceptionCode",
    "BaseExceptionCode",
    "ExceptionStatus",
    "ResponseModel",
    "register_exception_handlers",
    "set_default_http_codes",
    "logger",
    "APIResponse"
]


def register_exception_handlers(app: FastAPI,
                                use_response_model: bool = True,
                                use_fallback_middleware: bool = True):
    """
    Registers the APIException handler.

    Parameters:
    -----------
    app : FastAPI
        The FastAPI app or sub-app.
    use_response_model : bool, optional
        If True, uses ResponseModel (Pydantic) for responses.
        If False, uses raw dict format.
    use_fallback_middleware : bool, optional
        If True, adds a fallback middleware to catch unhandled exceptions.
        If False, only the APIException handler is registered.
    """

    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        logger.error(f"Exception handled for path: {request.url.path}")
        if use_response_model:
            content = exc.to_response_model().model_dump(exclude_none=False)
        else:
            content = exc.to_response()
        return JSONResponse(
            status_code=exc.http_status_code,
            content=content
        )

    if use_fallback_middleware:

        @app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request, exc):
            return JSONResponse(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                content=ResponseModel(
                    data=None,
                    status=ExceptionStatus.FAIL,
                    message="Validation Error",
                    error_code="VAL-422",
                    description="Input validation failed.",
                ).dict(),
            )


        @app.middleware("http")
        async def fallback_exception_middleware(request: Request,
                                                call_next: Callable):
            """
            Middleware to catch unhandled exceptions and log them.
            This middleware acts as a fallback for any unhandled exceptions that occur
            during request processing.
            It logs the exception details and returns a standardized error response.
            This is useful for catching unexpected errors that are not explicitly handled
            by the APIException handler.
            Parameters:
            ----------
            -----------
            request: Request
                The incoming request object.
            call_next: Callable
                The next middleware or endpoint to call.
            -----------

            Args:
                request:
                call_next:

            Returns:
                JSONResponse: A standardized error response with status code 500.

            """
            try:
                return await call_next(request)
            except Exception as e:
                tb = traceback.format_exc()
                logger.error("⚡ Unhandled Exception Fallback ⚡")
                logger.error(f"📌 Path: {request.url.path}")
                logger.error(f"📌 Method: {request.method}")
                logger.error(f"📌 Client IP: {request.client.host if request.client else 'unknown'}")
                logger.error(f"📌 Exception: {str(e)}")
                logger.error(f"📌 Traceback:\n{tb}")

                return JSONResponse(
                    status_code=500,
                    content=ResponseModel(
                        data=None,
                        status=ExceptionStatus.FAIL,
                        message="Something went wrong.",
                        error_code="ISE-500",
                        description="An unexpected error occurred. Please try again later."
                    ).model_dump(exclude_none=False)
                )
