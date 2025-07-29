from typing import Any, TypeVar, Optional
from pydantic import BaseModel


class ErrorValidation(BaseModel):
    """Represents a validation error detail."""

    field: str
    message: str


T = TypeVar("T")


def check_not_empty(value: T, field_name: Optional[str]) -> T:
    """
    Validates that a value is not None or empty.

    Args:
        value: The value to validate.
        field_name: The name of the field being validated.

    Returns:
        The original value if it's valid.

    Raises:
        ValueError: If the value is None or empty.
    """
    if value is None or value == "":
        raise ValueError(f"{field_name} cannot be empty")
    return value


def validate_uuid(value: str, field_name: str) -> str:
    """
    Validates that a string is a valid UUID (32 or 36 characters).

    Args:
        value: The string to validate.
        field_name: The name of the field being validated.

    Returns:
        The original string if it's a valid UUID.

    Raises:
        ValueError: If the string is not a valid UUID.
    """
    if not (len(value) in (32, 36) and value.replace("-", "").isalnum()):
        raise ValueError(f"{field_name} must be a valid 32 or 36 character UUID")
    return value
