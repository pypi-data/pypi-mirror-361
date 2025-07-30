# APIException for FastAPI
[![PyPI version](https://img.shields.io/pypi/v/APIException)](https://pypi.org/project/APIException/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**APIException** is a customizable exception-handling library designed for Python and FastAPI applications, offering standardized error codes, messages, and HTTP status responses to improve error management and consistency across APIs. This library is particularly suitable if you want to have control over the exceptions managed by the backend, ensuring a uniform response structure across your FastAPI endpoints.

[**View on PyPI**](https://pypi.org/project/APIException)

## Installation

To install APIException, run:

```bash
pip install APIException==0.1.9
```

## Features
- **Global Exception Handling**: Easily set up a global exception handler in FastAPI with @app.exception_handler(APIException) for consistent error responses across endpoints.
  
- **Backend-Controlled Exceptions**: This library is ideal if you want the backend to control the exceptions displayed to end-users, with customized codes, messages, and descriptions.

- **Standardized Error Handling**: APIException allows you to define a consistent format for error responses, making your API more predictable and easier to work with.

- **Customizable Codes & Statuses**: Extend BaseExceptionCode to define your own custom error codes. Override default HTTP status codes anytime with set_default_http_codes.

- **Response Model Consistency**: Use ResponseModel for both success and error responses to keep the same structure across your whole app.

- **HTTP Status Integration**: Set HTTP status codes alongside error messages, ensuring that API clients receive appropriate responses for different types of errors (e.g., 400 for client errors, 500 for server errors).

- **Automatic Logging**: Every APIException automatically logs the file, line number, the path, code, message, and description.

- **Multiple Apps**: You can register the same handler for multiple apps (mobile_app, admin_app, merchant_app).

- **Flexible Output**: Return raw dicts or Pydantic models — it’s up to you.

- **Extensible Error Codes**: Extend the `ExceptionCode` class to add custom error codes unique to your application’s needs.

- **Compatibility with FastAPI**: APIException integrates seamlessly with FastAPI, allowing you to standardize error responses across your endpoints.

- **Descriptive Responses**: Provides detailed descriptions for errors, making it easier for developers and users to understand the context of an error.


## Quickstart
### 1) Register the Handler
```bash
from api_exception import register_exception_handlers

register_exception_handlers(app)  # uses ResponseModel by default
```
Use raw dict instead:
```bash
register_exception_handlers(app, use_response_model=False)
```
### 2) Raise an APIException
```python
from api_exception import APIException, ExceptionCode, register_exception_handlers, ResponseModel
from fastapi import FastAPI

app = FastAPI()
register_exception_handlers(app) 

@app.get("/login")
async def login(username: str, password: str):
    if username != "admin" or password != "admin":
        raise APIException(
            error_code=ExceptionCode.AUTH_LOGIN_FAILED,
            http_status_code=401
        )
    return ResponseModel(data={"username": username})
```
Simple as that! Now, if the login fails, the APIException will be raised, and the global exception handler will return a standardized error response. Also, the exception will be logged automatically with details about where it was raised.
### 3) Success Response with ResponseModel
```python
from api_exception import ResponseModel

@app.get("/success")
async def success():
    return ResponseModel(
        data={"foo": "bar"},
        message="Everything went fine!"
    )
```

### 4) Custom Error Codes
Always extend BaseExceptionCode — don’t subclass ExceptionCode!
```python
from api_exception import BaseExceptionCode

class CustomExceptionCode(BaseExceptionCode):
    USER_NOT_FOUND = ("USR-404", "User not found.", "User does not exist.")
    INVALID_API_KEY = ("API-401", "Invalid API key.", "Key missing or invalid.")
```
Use it:
```python
from api_exception import APIException, ExceptionCode, register_exception_handlers, ResponseModel
from fastapi import FastAPI

app = FastAPI()
register_exception_handlers(app) 
@app.get("/user/{user_id}")
async def get_user(user_id: int):
    if user_id != 1:
        raise APIException(
            error_code=ExceptionCode.USER_NOT_FOUND,
            http_status_code=404
        )
    return ResponseModel(data={"user_id": user_id})
```

## 5) Override Default HTTP Status Codes


```python
from api_exception import set_default_http_codes

set_default_http_codes({
    "FAIL": 422,
    "WARNING": 202
})
```

## 6) Multiple Apps? No Problem
```python
from fastapi import FastAPI
from api_exception import register_exception_handlers
mobile_app = FastAPI()
admin_app = FastAPI()
merchant_app = FastAPI()
register_exception_handlers(mobile_app)
register_exception_handlers(admin_app)
register_exception_handlers(merchant_app)
```

## 7) Automatic Logging

Each APIException automatically logs:

	•	File name and line number.
	•	Error code, status, message, description.

Use the built-in logger for your own logs too:
```python
from api_exception import logger

logger.info("Custom info log")
logger.error("Custom error log")
```

# Installation

### Step 1: Install the Package

Install the package via pip:

```bash
pip install APIException
```
### Step 2: Import and Use in Your FastAPI Project
The following example demonstrates how to use APIException in a FastAPI endpoint.

```python
from api_exception import APIException, ExceptionCode, register_exception_handlers, ResponseModel
from fastapi import FastAPI

app = FastAPI()
register_exception_handlers(app) 

@app.get("/login")
async def login(username: str, password: str):
    if username != "admin" or password != "admin":
        raise APIException(
            error_code=ExceptionCode.AUTH_LOGIN_FAILED,
            http_status_code=401,
            message="Invalid credentials provided.",
            description="The provided username or password is incorrect. Please try again.",
        )
    return ResponseModel(data={"username": username})
```



## Testing the APIException Library
You can test the library by writing unit tests. Here’s an example of how you might structure tests for the APIException library.
```python
import unittest
from api_exception.exception import APIException
from custom_enum.enums import ExceptionCode, ExceptionStatus
from schemas.response_model import ResponseModel

class TestAPIException(unittest.TestCase):

    def test_api_exception(self):
        exception = APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED)
        self.assertEqual(exception.error_code, "AUTH-1000")
        self.assertEqual(exception.message, "Incorrect username and password.")
        self.assertEqual(exception.description, "Failed authentication attempt.")
        self.assertEqual(exception.status, ExceptionStatus.FAIL)
        self.assertEqual(exception.http_status_code, 400)

        # Test the response dictionary
        response = exception.to_response()
        expected_response = {
            "error_code": "AUTH-1000",
            "status": "FAIL",
            "message": "Incorrect username and password.",
            "description": "Failed authentication attempt"
        }
        self.assertEqual(response, expected_response)

    def test_response_model(self):
        response = ResponseModel(data={"key": "value"})
        self.assertEqual(response.status, ExceptionStatus.SUCCESS)
        self.assertEqual(response.message, "Operation completed successfully.")
        self.assertIsNone(response.error_code)
        self.assertIsNone(response.description)
        self.assertEqual(response.data, {"key": "value"})

if __name__ == "__main__":
    unittest.main()
```
This test case verifies that the APIException class behaves as expected, including proper response formatting and attribute assignments.
### Run the Tests
To run the tests, you can use the following command in your terminal:

```bash
python -m unittest discover -s tests
```

## Changelog

### v0.1.8 (2025-13-07)
- Added CLI entrypoint (`api_exception-info`)
- Improved README structure and examples
- Stable test suite with FastAPI `TestClient`
- Multiple apps support, raw or ResponseModel output
- Register Exception Handlers by calling `register_exception_handlers(app)` in your FastAPI app
- Automatic logging of APIException details
- __all__ has been updated to include all public classes and functions

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue to improve this library. Follow the guidelines below:

	1.	Fork the repository.
	2.	Create a new branch.
	3.	Make your changes and ensure all tests pass.
	4.	Submit a pull request with a detailed description of the changes.

## Why Use APIException?

If you want to control the exceptions shown to end-users from the backend, APIException is a powerful choice. With it, you can define and manage error codes, messages, and descriptions directly in the backend, creating a cohesive and predictable error-handling system. The flexibility to create custom error codes and the integration with FastAPI’s global exception handling makes it easy to apply standardized error responses across your API.

## License
This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.
If you like this library and find it useful, don’t forget to give it a ⭐ on GitHub!

## Contact
If you have any questions or suggestions, please feel free to reach out at [ahmetkutayural.dev](https://ahmetkutayural.dev/#contact)


