from typing import Optional

from pydantic import UUID4, BaseModel, Field, ValidationInfo, field_validator

from carestack.common.error_validation import check_not_empty
from carestack.document_linking.encounter_dto.target_dto.health_information_dto import (
    HealthInformationDTO,
)


class UpdateVisitRecordsDTO(BaseModel):
    """Represents data for updating visit records."""

    care_context_reference: str = Field(..., alias="careContextReference")
    patient_reference: str = Field(..., alias="patientReference")
    practitioner_reference: str = Field(..., alias="practitionerReference")
    appointment_reference: str = Field(..., alias="appointmentReference")
    patient_abha_address: Optional[str] = Field(None, alias="patientAbhaAddress")
    health_records: list[HealthInformationDTO] = Field(..., alias="healthRecords")
    mobile_number: Optional[str] = Field(None, alias="mobileNumber")
    request_id: Optional[str] = Field(None, alias="requestId")

    # @field_validator(
    #     "care_context_reference",
    #     "appointment_reference",
    #     "patient_reference",
    #     "practitioner_reference",
    # )
    # @classmethod
    # def _validate_fields(cls, v: str, info: ValidationInfo) -> str:
    #     """Validates that required fields are not empty."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("health_records")
    # @classmethod
    # def _health_records_not_empty(
    #     cls, v: list[HealthInformationDTO]
    # ) -> list[HealthInformationDTO]:
    #     """Validates that the health records list is not empty."""
    #     return check_not_empty(v, "health records list")

    # @field_validator("mobile_number")
    # @classmethod
    # def _mobile_number_format(cls, v: Optional[str]) -> Optional[str]:
    #     """
    #     Validates that the mobile number does not contain '*' characters when provided.
    #     """
    #     if v and "*" in v:
    #         raise ValueError("Mobile number cannot contain * characters")
    #     return v


class UpdateVisitRecordsResponse(BaseModel):
    success: bool
