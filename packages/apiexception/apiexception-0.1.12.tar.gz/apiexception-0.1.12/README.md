# APIException for FastAPI
[![PyPI version](https://img.shields.io/pypi/v/APIException?cacheSeconds=60)](https://pypi.org/project/APIException/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://akutayural.github.io/APIException/)

**APIException** is a fully extensible exception-handling library for **FastAPI**, designed to help you **standardize error responses**, **manage custom error codes**, and ensure **predictable, well-documented APIs** — from day one.

- 🔒 Consistent JSON responses for **both** success and errors.
- 📚 Beautiful Swagger/OpenAPI documentation with clear error cases.
- ⚙️ Customizable error codes with `BaseExceptionCode`.
- 🔗 Global fallback for unhandled server-side errors.
- 🗂️ Use with **multiple FastAPI apps**.
- 📜 Automatic logging of every exception detail.
- ✔️ Production-ready with unit test examples.

· [**View on PyPI**](https://pypi.org/project/APIException) 

· [**Full Documentation**](https://akutayural.github.io/APIException/)

Reading the [full documentation](https://akutayural.github.io/APIException/) is **highly recommended** — it’s clear, thorough, and helps you get started in minutes.

---

## 📦 Installation

```bash
pip install APIException==0.1.12
```
## ⚡ Quickstart

**1️⃣ Register the Handler**

```python
from APIException import register_exception_handlers
from fastapi import FastAPI

app = FastAPI()
register_exception_handlers(app)  # uses ResponseModel by default

# Use raw dict instead:
# register_exception_handlers(app, use_response_model=False)
```

---

**2️⃣ Raise an Exception**

```python
from APIException import APIException, ExceptionCode, register_exception_handlers
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
    return {"message": "Login successful!"}
```

---

**3️⃣ Use ResponseModel for Success Responses**

```python
from APIException import ResponseModel, register_exception_handlers
from fastapi import FastAPI
app = FastAPI()

register_exception_handlers(app)

@app.get("/success")
async def success():
    return ResponseModel(
        data={"foo": "bar"},
        message="Everything went fine!"
    )
```

---

## 🧩 Custom Error Codes

Always extend BaseExceptionCode — don’t subclass ExceptionCode directly!

```python
from APIException import BaseExceptionCode

class CustomExceptionCode(BaseExceptionCode):
    USER_NOT_FOUND = ("USR-404", "User not found.", "User does not exist.")
    INVALID_API_KEY = ("API-401", "Invalid API key.", "Key missing or invalid.")
```

And use it:

```python
from APIException import APIException

raise APIException(
    error_code=CustomExceptionCode.USER_NOT_FOUND,
    http_status_code=404
)
```

---

## ⚙️ Override Default HTTP Status Codes

```python
from APIException import set_default_http_codes

set_default_http_codes({
    "FAIL": 422,
    "WARNING": 202
})
```

---

## 🌐 Multiple Apps Support
```python
from fastapi import FastAPI
from APIException import register_exception_handlers

mobile_app = FastAPI()
admin_app = FastAPI()
merchant_app = FastAPI()

register_exception_handlers(mobile_app)
register_exception_handlers(admin_app)
register_exception_handlers(merchant_app)
```

---

## 📝 Automatic Logging

Every APIException automatically logs:

- File name & line number

- Error code, status, message, description

Or use the built-in logger:

```python
from APIException import logger

logger.info("Custom info log")
logger.error("Custom error log")
```

---

## ✅ Testing Example

```python
import unittest
from APIException import APIException, ExceptionCode, ResponseModel

class TestAPIException(unittest.TestCase):
    def test_api_exception(self):
        exc = APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED)
        self.assertEqual(exc.status.value, "FAIL")

    def test_response_model(self):
        res = ResponseModel(data={"foo": "bar"})
        self.assertEqual(res.status.value, "SUCCESS")

if __name__ == "__main__":
    unittest.main()
```

**Run the Tests**
- To run the tests, you can use the following command in your terminal:

```bash
python -m unittest discover -s tests
```

---

## 🔗 Full Documentation

Find detailed guides and examples in the official docs.

---

## 📜 Changelog

**v0.1.12 (2025-07-14)**

- /examples/fastapi_usage.py has been updated.

- 422 Pydantic error has been handled in register_handler

- Documentation has been added.

- `use_fallback_middleware` has been added.

**v0.1.11 (2025-07-13)**

- Added CLI entrypoint (api_exception-info)

- Stable test suite with FastAPI TestClient

- Multiple app support

- Raw dict or Pydantic output

- Automatic logging improvements

---

## License
This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.
If you like this library and find it useful, don’t forget to give it a ⭐ on GitHub!

## Contact
If you have any questions or suggestions, please feel free to reach out at [ahmetkutayural.dev](https://ahmetkutayural.dev/#contact)


