from pydantic import Field, ValidationInfo, field_validator

from carestack.common.enums import ClinicalStatus
from carestack.common.error_validation import check_not_empty
from carestack.document_linking.encounter_dto.target_dto.snomed_code_dto import (
    SnomedCode,
)


class Condition(SnomedCode):
    """Represents a medical condition."""

    clinical_status: ClinicalStatus = Field(..., alias="clinicalStatus")

    # @field_validator("clinical_status")
    # @classmethod
    # def _validate_clinical_field(cls, v: str, info: ValidationInfo) -> str:
    #     """Validates that the clinical status is not empty."""
    #     return check_not_empty(v, info.field_name)
