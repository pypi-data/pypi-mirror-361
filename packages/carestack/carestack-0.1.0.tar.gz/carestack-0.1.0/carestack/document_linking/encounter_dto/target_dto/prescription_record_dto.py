from typing import Optional
from pydantic import BaseModel, Field, field_validator

from carestack.common.error_validation import check_not_empty
from carestack.document_linking.encounter_dto.target_dto.document_reference_dto import (
    DocumentReference,
)
from carestack.document_linking.encounter_dto.target_dto.medication_request_dto import (
    MedicationRequest,
)
from carestack.document_linking.encounter_dto.target_dto.observation_dto import (
    Observation,
)
from carestack.document_linking.encounter_dto.target_dto.condition_dto import (
    Condition,
)


class PrescriptionRecordDTO(BaseModel):
    """Represents a prescription record."""

    medication_requests: Optional[list[MedicationRequest]] = Field(
        None, alias="medicationRequests"
    )
    prescription_binaries: list[DocumentReference] = Field(
        ..., alias="prescriptionBinaries"
    )
    conditions: Optional[list[Condition]] = Field(None, alias="conditions")
    physical_examination: Optional[list[Observation]] = Field(
        None, alias="physicalExamination"
    )

    # @field_validator("prescription_binaries")
    # @classmethod
    # def _prescription_binaries_not_empty(
    #     cls, v: list[DocumentReference]
    # ) -> list[DocumentReference]:
    #     """Validates that the prescription binaries list is not empty."""
    #     return check_not_empty(v, "prescription binaries list")
