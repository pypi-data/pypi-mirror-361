from pydantic import BaseModel, Field, ValidationInfo, field_validator

from carestack.common.error_validation import check_not_empty
from carestack.document_linking.encounter_dto.target_dto.snomed_code_dto import (
    SnomedCode,
)


class AdvisoryNote(BaseModel):
    """Represents an advisory note with category and note."""

    category: SnomedCode = Field(...)
    note: SnomedCode = Field(...)

    # @field_validator("category", "note")
    # @classmethod
    # def _validate_fields(cls, v: SnomedCode, info: "ValidationInfo") -> SnomedCode:
    #     """Validates that required fields are not empty."""
    #     return check_not_empty(v, info.field_name)
