from typing import Optional


class EhrApiError(Exception):
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        code: Optional[str] = None,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"


class AuthenticationError(EhrApiError):
    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, 401)
        self.name = "AuthenticationError"


class ValidationError(EhrApiError):
    def __init__(self, message: str) -> None:
        super().__init__(message, 400)
        self.name = "ValidationError"
