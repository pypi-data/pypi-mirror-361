from typing import Any, Optional

from pydantic import UUID4, BaseModel, Field, ValidationInfo, field_validator

from carestack.common.enums import AuthMode, HealthInformationTypes
from carestack.common.error_validation import check_not_empty


class CreateCareContextDTO(BaseModel):
    """Represents the data for creating a care context."""

    patient_reference: str = Field(..., alias="patientReference")
    patient_abha_address: Optional[str] = Field(None, alias="patientAbhaAddress")
    practitioner_reference: str = Field(..., alias="practitionerReference")
    appointment_reference: str = Field(..., alias="appointmentReference")
    hi_type: HealthInformationTypes = Field(..., alias="hiType")
    appointment_date: str = Field(..., alias="appointmentDate")
    resend_otp: bool = Field(..., alias="resendOtp")

    # @field_validator(
    #     "appointment_reference",
    #     "appointment_date",
    #     "patient_reference",
    #     "practitioner_reference",
    # )
    # @classmethod
    # def _validate_fields(cls, v: Any, info: ValidationInfo) -> Any:
    #     """Validates that required fields are not empty."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("hi_type")
    # @classmethod
    # def _hi_type_not_empty(
    #     cls, v: HealthInformationTypes, info: ValidationInfo
    # ) -> HealthInformationTypes:
    #     """Validates that the HI type is not empty."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("resend_otp")
    # @classmethod
    # def _validate_resend_otp(cls, v: bool, info: ValidationInfo) -> bool:
    #     """Validates that required fields are not empty."""
    #     return check_not_empty(v, info.field_name)


class CreateCareContextResponse(BaseModel):
    care_context_reference: str = Field(..., alias="careContextReference")
    request_id: str = Field(..., alias="requestId")
    auth_modes: list[AuthMode] = Field(..., alias="authModes")
