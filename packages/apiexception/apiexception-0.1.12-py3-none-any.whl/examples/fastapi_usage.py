from fastapi import FastAPI, Path
from pydantic import BaseModel
from api_exception import (
    APIException,
    ExceptionStatus,
    BaseExceptionCode,
    ResponseModel,
    register_exception_handlers,
    APIResponse,
)

app = FastAPI()
register_exception_handlers(app)


class CustomExceptionCode(BaseExceptionCode):
    USER_NOT_FOUND = ("USR-404", "User not found.", "The user ID does not exist.")
    INVALID_API_KEY = ("API-401", "Invalid API key.", "Provide a valid API key.")
    PERMISSION_DENIED = ("PERM-403", "Permission denied.", "Access to this resource is forbidden.")
    VALIDATION_ERROR = ("VAL-422", "Validation Error", "Input validation failed.")


@app.get(
    "/user/{user_id}",
    response_model=ResponseModel,
    responses=APIResponse.custom(
        (404, CustomExceptionCode.USER_NOT_FOUND),
        (422, CustomExceptionCode.VALIDATION_ERROR)
    )
)
async def get_user(user_id: int = Path(..., description="The ID of the user")):
    if user_id != 1:
        raise APIException(
            error_code=CustomExceptionCode.USER_NOT_FOUND,
            http_status_code=404,
        )
    return ResponseModel(data={"user_id": user_id, "name": "John Doe"})


@app.get(
    "/apikey",
    response_model=ResponseModel,
    responses=APIResponse.custom(
        (401, CustomExceptionCode.INVALID_API_KEY),
        (422, CustomExceptionCode.VALIDATION_ERROR)
    )
)
async def check_api_key(api_key: str):
    if api_key != "valid_key":
        raise APIException(
            error_code=CustomExceptionCode.INVALID_API_KEY,
            http_status_code=401,
        )
    return ResponseModel(
        data={"api_key": api_key},
        status=ExceptionStatus.SUCCESS,
        message="API key is valid",
        description="The provided API key is valid."
    )


class UserResponse(BaseModel):
    id: int
    username: str


@app.get(
    "/user-basic",
    response_model=ResponseModel[UserResponse],
    responses=APIResponse.custom(
        (401, CustomExceptionCode.INVALID_API_KEY),
        (403, CustomExceptionCode.PERMISSION_DENIED),
        (422, CustomExceptionCode.VALIDATION_ERROR)
    ),
)
async def user_basic():
    is_not_allowed = True
    if is_not_allowed:
        raise APIException(
            error_code=CustomExceptionCode.PERMISSION_DENIED,
            http_status_code=403,
        )
    data = UserResponse(id=1, username="Kutay")
    return ResponseModel[UserResponse](
        data=data,
        description="User retrieved successfully."
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)