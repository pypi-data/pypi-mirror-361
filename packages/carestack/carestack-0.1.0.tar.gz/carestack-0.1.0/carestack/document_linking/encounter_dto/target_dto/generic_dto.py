from pydantic import BaseModel, Field, ValidationInfo, field_validator

from carestack.common.error_validation import check_not_empty


class GenericCode(BaseModel):
    """Represents a generic code with system, code, and text properties."""

    system: str = Field(..., alias="system")
    code: str = Field(..., alias="code")
    text: str = Field(..., alias="text")

    # @field_validator("system", "code", "text")
    # def _validate_fields(cls, v: str, info: ValidationInfo) -> str:
    #     """Validates that the provided field is not empty."""
    #     return check_not_empty(v, info.field_name)
