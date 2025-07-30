from typing import Optional

from pydantic import BaseModel


class ErrorBase(BaseModel):
    error: str
    message: str
    code: Optional[int] = None

    def string(self) -> str:
        prefix = f"{self.code} - " if self.code else ""
        return f"{prefix}{self.error}: {self.message}"

    def __str__(self) -> str:
        return self.string()

    def __int__(self) -> int:
        if self.code is None:
            raise ValueError("Error code is not set")
        return self.code


class Error(ErrorBase):
    """Error model for the Ambient Event Bus Client.

    Attributes:
        - error: str - The error type.
        - message: str - The error message.
        - code: int - The error code.
    """
