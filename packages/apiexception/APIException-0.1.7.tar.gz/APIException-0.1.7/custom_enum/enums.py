from enum import Enum


class ExceptionStatus(str, Enum):
    """
    Enum for different exception statuses used in APIException.
    Provides a standardized way to indicate the outcome of operations.
    """
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    FAIL = "FAIL"


class BaseExceptionCode(Enum):
    """
    Base class for defining standardized exception codes and messages.

    Each exception code should include:
    - error_code: Unique identifier for the error.
    - message: User-friendly description of the error.
    - description: Optional detailed description for additional context.
    """

    @property
    def error_code(self):
        return self.value[0]

    @property
    def message(self):
        return self.value[1]

    @property
    def description(self):
        return self.value[2] if len(self.value) > 2 else ""


class ExceptionCode(BaseExceptionCode):
    """
    Standardized exception codes for common errors.

    Each exception code entry should provide:
    - A unique error identifier.
    - A user-friendly message.
    - An optional description for more context.
    """
    AUTH_LOGIN_FAILED = ("AUTH-1000", "Incorrect username and password.", "Failed authentication attempt.")
    EMAIL_ALREADY_TAKEN = (
        "RGST-1000", "An account with this email already exists.", "Duplicate email during registration.")
    # Add other exceptions with descriptions as needed
