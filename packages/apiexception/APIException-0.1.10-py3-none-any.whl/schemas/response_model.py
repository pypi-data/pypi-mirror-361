from typing import Generic, TypeVar, Optional
from pydantic import BaseModel
from custom_enum.enums import ExceptionStatus

# Generic type for response data
DataT = TypeVar('DataT')


class ResponseModel(BaseModel, Generic[DataT]):
    """
    Pydantic model for standardizing successful API responses.

    Attributes:
    -----------
    - data : Optional[DataT]
        The main content of the response.
    - status : ExceptionStatus
        The status of the response, defaults to SUCCESS.
    - message : str
        Message providing additional context, defaults to a generic success message.
    - error_code : Optional[str]
        Optional error code, typically None for successful responses.
    - description : Optional[str]
        Optional detailed description of the response.
    """
    data: Optional[DataT] = None
    status: ExceptionStatus = ExceptionStatus.SUCCESS
    message: str = 'Operation completed successfully.'
    error_code: Optional[str] = None
    description: Optional[str] = None
