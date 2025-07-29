from pydantic import Field, ValidationInfo, field_validator

from carestack.common.enums import ClinicalStatus, VerificationStatus
from carestack.common.error_validation import check_not_empty
from carestack.document_linking.encounter_dto.target_dto.snomed_code_dto import (
    SnomedCode,
)


class AllergyIntolerance(SnomedCode):
    """Represents an allergy intolerance record."""

    clinical_status: ClinicalStatus = Field(..., alias="clinicalStatus")
    verification_status: VerificationStatus = Field(..., alias="verificationStatus")
    recorded_date: str = Field(..., alias="recordedDate")
    reaction: str = Field(..., alias="reaction")

    # @field_validator("clinical_status")
    # @classmethod
    # def _clinical_status_not_empty(
    #     cls,
    #     v: ClinicalStatus,
    #     info: ValidationInfo,
    # ) -> ClinicalStatus:
    #     """Validates that the clinical status is not empty."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("verification_status")
    # @classmethod
    # def _verification_status_not_empty(
    #     cls,
    #     v: VerificationStatus,
    #     info: ValidationInfo,
    # ) -> VerificationStatus:
    #     """Validates that the verification status is not empty."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("recorded_date", "reaction")
    # @classmethod
    # def _recorded_date_not_empty(cls, v: str, info: ValidationInfo) -> str:
    #     """Validates that required fields are not empty."""
    #     return check_not_empty(v, info.field_name)
