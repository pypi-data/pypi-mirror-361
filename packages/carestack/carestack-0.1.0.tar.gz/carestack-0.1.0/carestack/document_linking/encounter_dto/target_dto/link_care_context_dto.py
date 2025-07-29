from pydantic import BaseModel, Field, ValidationInfo, field_validator

from carestack.common.enums import AuthMode
from carestack.common.error_validation import check_not_empty


class LinkCareContextDTO(BaseModel):
    """Represents data for linking a care context."""

    request_id: str = Field(..., alias="requestId")
    appointment_reference: str = Field(..., alias="appointmentReference")
    patient_address: str = Field(..., alias="patientAddress")
    patient_name: str = Field(..., alias="patientName")
    patient_reference: str = Field(..., alias="patientReference")
    care_context_reference: str = Field(..., alias="careContextReference")
    auth_mode: AuthMode = Field(..., alias="authMode")

    # @field_validator(
    #     "request_id",
    #     "appointment_reference",
    #     "patient_address",
    #     "patient_name",
    #     "patient_reference",
    #     "care_context_reference",
    # )
    # @classmethod
    # def _validate_fields(cls, v: str, info: ValidationInfo) -> str:
    #     """Validates that required fields are not empty."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("auth_mode")
    # @classmethod
    # def _validate_auth_mode(cls, v: AuthMode, info: ValidationInfo) -> AuthMode:
    #     """Validates that the auth mode is not empty."""
    #     return check_not_empty(v, info.field_name)
