import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api_exception import (
    APIException,
    ExceptionCode,
    ExceptionStatus,
    ResponseModel,
    register_exception_handlers,
    set_default_http_codes
)


class TestAPIException(unittest.TestCase):

    def test_api_exception_default(self):
        exception = APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED)
        self.assertEqual(exception.error_code, "AUTH-1000")
        self.assertEqual(exception.message, "Incorrect username and password.")
        self.assertEqual(exception.description, "Failed authentication attempt.")
        self.assertEqual(exception.status, ExceptionStatus.FAIL)
        self.assertEqual(exception.http_status_code, 400)

    def test_api_exception_custom_message(self):
        custom_message = "Custom error message."
        exception = APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED, message=custom_message)
        self.assertEqual(exception.message, custom_message)

    def test_api_exception_custom_description(self):
        custom_description = "Custom description."
        exception = APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED, description=custom_description)
        self.assertEqual(exception.description, custom_description)

    def test_api_exception_custom_status_code(self):
        custom_status_code = 403
        exception = APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED, http_status_code=custom_status_code)
        self.assertEqual(exception.http_status_code, custom_status_code)

    def test_api_exception_to_response(self):
        exception = APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED)
        response = exception.to_response()
        self.assertEqual(response["error_code"], "AUTH-1000")
        self.assertEqual(response["status"], "FAIL")

    def test_api_exception_to_response_model(self):
        exception = APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED)
        response_model = exception.to_response_model()
        self.assertEqual(response_model.status, ExceptionStatus.FAIL)
        self.assertEqual(response_model.message, "Incorrect username and password.")

    def test_response_model_success(self):
        response = ResponseModel(data={"key": "value"})
        self.assertEqual(response.status, ExceptionStatus.SUCCESS)
        self.assertIsNone(response.error_code)
        self.assertEqual(response.data, {"key": "value"})

    def test_response_model_with_custom_message(self):
        response = ResponseModel(data={"key": "value"}, message="Custom success message.")
        self.assertEqual(response.message, "Custom success message.")

    def test_response_model_with_error(self):
        response = ResponseModel(
            data=None,
            status=ExceptionStatus.FAIL,
            message="An error occurred.",
            error_code="AUTH-1000",
            description="Failed authentication attempt"
        )
        self.assertEqual(response.status, ExceptionStatus.FAIL)
        self.assertEqual(response.message, "An error occurred.")
        self.assertEqual(response.error_code, "AUTH-1000")

    def test_set_default_http_codes(self):
        new_map = {ExceptionStatus.FAIL: 500}
        set_default_http_codes(new_map)
        exception = APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED)
        self.assertEqual(exception.http_status_code, 400)
        exception2 = APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED, http_status_code=None)
        self.assertEqual(exception2.http_status_code, 500)

    def test_register_exception_handlers_with_fastapi(self):
        app = FastAPI()
        register_exception_handlers(app)

        @app.get("/test")
        def test_endpoint():
            raise APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED)

        client = TestClient(app)
        response = client.get("/test")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error_code"], "AUTH-1000")
        self.assertEqual(response.json()["status"], "FAIL")

    def test_register_exception_handlers_raw_response(self):
        app = FastAPI()
        register_exception_handlers(app, use_response_model=False)

        @app.get("/test-raw")
        def test_endpoint():
            raise APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED)

        client = TestClient(app)
        response = client.get("/test-raw")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error_code"], "AUTH-1000")
        self.assertIn("message", response.json())


if __name__ == "__main__":
    unittest.main()