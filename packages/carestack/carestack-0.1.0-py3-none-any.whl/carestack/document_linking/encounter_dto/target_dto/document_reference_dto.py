from pydantic import BaseModel, Field, ValidationInfo, field_validator

from carestack.common.error_validation import check_not_empty


class DocumentReference(BaseModel):
    """Represents a document reference."""

    content_type: str = Field(..., alias="contentType")
    data: str = Field(..., alias="data")

    # @field_validator("content_type", "data")
    # @classmethod
    # def _validate_fields(cls, v: str, info: ValidationInfo) -> str:
    #     """Validates that required fields are not empty."""
    #     return check_not_empty(v, info.field_name)
