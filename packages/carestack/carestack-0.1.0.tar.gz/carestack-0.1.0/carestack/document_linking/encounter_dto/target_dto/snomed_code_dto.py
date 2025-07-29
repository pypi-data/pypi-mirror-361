from pydantic import BaseModel, Field, RootModel, ValidationInfo, field_validator

from carestack.common.error_validation import check_not_empty


class SnomedCode(BaseModel):
    """Represents a SNOMED code."""

    code: str = Field(..., description="The SNOMED code.")
    text: str = Field(..., description="The text description.")

    # @field_validator("code", "text")
    # @classmethod
    # def _validate_fields(cls, v: str, info: ValidationInfo) -> str:
    #     """Validates that required fields are not empty."""
    #     return check_not_empty(v, info.field_name)


class ClosestTerm(BaseModel):
    term: str
    code: str
    min_distance: int


class SearchResultResponse(BaseModel):
    term: str
    code: str


class SearchResultListResponse(RootModel):
    root: list[SearchResultResponse]
