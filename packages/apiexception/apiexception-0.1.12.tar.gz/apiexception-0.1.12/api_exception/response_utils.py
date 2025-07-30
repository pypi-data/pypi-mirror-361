from typing import Dict
from schemas.response_model import ResponseModel
from custom_enum.enums import ExceptionCode, ExceptionStatus, BaseExceptionCode


class APIResponse:
    """
    Utility class to generate standardized Swagger/OpenAPI responses
    using your ResponseModel for both default and custom errors.
    """

    @staticmethod
    def default() -> Dict[int, dict]:
        """
        Generate default standardized error responses for common HTTP status codes.

        Each response uses your ResponseModel with:
            - 'status' set to FAIL
            - 'data' always set to None since we are dealing with the error cases.
            - 'message', 'description' and 'error_code' specific to the status code

        Useful for quickly adding 400, 401, 403, 404, 500 standard error examples
        to your FastAPI route docs.

        Example:
            responses = APIResponse.default()

        Returns:
            Dict[int, dict]: A dictionary mapping each status code to a
            Swagger/OpenAPI response object that FastAPI can use in the 'responses' parameter.
        """
        examples = {
            400: ("BAD-400", "Bad Request", "Your request is invalid or malformed."),
            401: ("AUTH-401", "Unauthorized", "Authentication credentials were missing or invalid."),
            403: ("PERM-403", "Forbidden", "You do not have permission to access this resource."),
            404: ("RES-404", "Not Found", "The requested resource could not be found."),
            500: ("INT-500", "Internal Server Error", "An unexpected error occurred on the server.")
        }

        responses = {}
        for code, (err_code, msg, desc) in examples.items():
            example = ResponseModel(
                data=None,
                status=ExceptionStatus.FAIL,
                message=msg,
                description=desc,
                error_code=err_code
            ).model_dump()

            responses[code] = {
                "model": ResponseModel,
                "description": msg,
                "content": {
                    "application/json": {
                        "example": example
                    }
                }
            }

        return responses

    @staticmethod
    def custom(*items: tuple[int, 'BaseExceptionCode']):
        """
        Generate one or more custom error responses for FastAPI Swagger docs
        using your defined ExceptionCode enums.

        Each custom response will use your standardized ResponseModel
        with FAIL status, the specified error_code, message, and description.
        The 'data' field will always be None for error cases.

        Args:
            *items: One or more tuples of (HTTP status code, ExceptionCode).
                - status_code (int): The HTTP status code to return.
                - exception_code (BaseExceptionCode): Your custom ExceptionCode entry.

        Example:
        ```python
            from custom_enum.enums import CustomExceptionCode
            from api_exception.response_utils import APIResponse
            responses = APIResponse.custom(
                (403, CustomExceptionCode.PERMISSION_DENIED),
                (401, CustomExceptionCode.INVALID_API_KEY)
            )
        ```

        Returns:
            Dict[int, dict]: A dictionary of status code to response spec,
            ready to be used in FastAPI route 'responses' parameter.
        """
        if not items:
            raise ValueError("At least one (status_code, exception_code) pair must be provided.")
        if not all(isinstance(item, tuple) and len(item) == 2 for item in items):
            raise ValueError("Each item must be a tuple of (status_code, exception_code).")
        if not all(isinstance(item[1], BaseExceptionCode) for item in items):
            raise ValueError("Each exception_code must be an instance of BaseExceptionCode or its subclass.")
        if not all(isinstance(item[0], int) for item in items):
            raise ValueError("Each status_code must be an integer.")

        responses = {}
        for status_code, exception_code in items:
            example = ResponseModel(
                data=None,
                status=ExceptionStatus.FAIL,
                message=exception_code.message,
                description=exception_code.description,
                error_code=exception_code.error_code
            ).model_dump()

            responses[status_code] = {
                "description": f"Status: {status_code} - {exception_code.error_code}",
                "content": {
                    "application/json": {
                        "example": example
                    }
                }
            }
        return responses
