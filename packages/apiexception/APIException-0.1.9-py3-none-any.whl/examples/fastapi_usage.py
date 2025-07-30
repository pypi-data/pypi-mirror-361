from fastapi import FastAPI, Request
from api_exception import (
    APIException,
    ExceptionStatus,
    BaseExceptionCode,
    ResponseModel,
    register_exception_handlers
)

app = FastAPI()

# register default HTTP status codes for APIException
register_exception_handlers(app)  # Default: use_response_model=True


# Define a custom ExceptionCode class for specific application errors
class CustomExceptionCode(BaseExceptionCode):
    USER_NOT_FOUND = ("USR-404", "User not found.", "The specified user does not exist in the system.")
    INVALID_API_KEY = ("API-401", "Invalid API key provided.", "Please provide a valid API key.")
    PERMISSION_DENIED = ("PERM-403", "Permission denied.", "You do not have permission to access this resource.")


@app.get("/user/{user_id}")
async def get_user(user_id: int):
    if user_id != 1:
        raise APIException(
            error_code=CustomExceptionCode.USER_NOT_FOUND,
            http_status_code=404
        )
    return ResponseModel(data={"user_id": user_id, "name": "John Doe"})


@app.get("/apikey")
async def check_api_key(api_key: str):
    if api_key != "valid_key":
        raise APIException(error_code=CustomExceptionCode.INVALID_API_KEY)
    # Uncomment below line if you want to use ResponseModel with default status
    # return ResponseModel(data={"message": "API key is valid"})
    return ResponseModel(data={"user": "xxx"}, status=ExceptionStatus.SUCCESS, message="API key is valid",
                         description="The provided API key is valid.")


@app.get("/restricted")
async def restricted_access():
    raise APIException(
        error_code=CustomExceptionCode.PERMISSION_DENIED,
        http_status_code=403,
        status=ExceptionStatus.FAIL,
        description="You do not have permission to access this resource.",
        message="Permission denied."
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
