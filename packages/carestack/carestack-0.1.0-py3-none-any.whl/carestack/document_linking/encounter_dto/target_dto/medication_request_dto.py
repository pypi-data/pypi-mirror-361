from typing import Optional
from pydantic import Field, ValidationInfo, field_validator

from carestack.common.enums import MedicationRequestStatus
from carestack.common.error_validation import check_not_empty
from carestack.document_linking.encounter_dto.target_dto.dosage_instruction_dto import (
    DosageInstruction,
)
from carestack.document_linking.encounter_dto.target_dto.snomed_code_dto import (
    SnomedCode,
)


class MedicationRequest(SnomedCode):
    """Represents a medication request."""

    status: MedicationRequestStatus = Field(..., alias="status")
    authored_on: str = Field(..., alias="authoredOn")
    dosage_instruction: DosageInstruction = Field(..., alias="dosageInstruction")
    medication: SnomedCode = Field(alias="medication")
    reason_code: SnomedCode = Field(alias="reasonCode")

    # @field_validator("status")
    # @classmethod
    # def _status_not_empty(
    #     cls, v: MedicationRequestStatus, info: ValidationInfo
    # ) -> MedicationRequestStatus:
    #     """Validates that the status is not empty."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("authored_on")
    # @classmethod
    # def _authored_on_not_empty(cls, v: str, info: ValidationInfo) -> str:
    #     """Validates that the authored on date is not empty."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("dosage_instruction")
    # @classmethod
    # def _dosage_instruction_not_empty(
    #     cls, v: DosageInstruction, info: ValidationInfo
    # ) -> DosageInstruction:
    #     """Validates that the dosage instruction is not empty."""
    #     return check_not_empty(v, info.field_name)
