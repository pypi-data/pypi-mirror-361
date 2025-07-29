from typing import Any, Optional, Union
from pydantic import BaseModel, Field, ValidationInfo, field_validator

from carestack.common.enums import AppointmentPriority
from carestack.common.error_validation import check_not_empty


class AppointmentDTO(BaseModel):
    """Represents an appointment."""

    practitioner_reference: str = Field(..., alias="practitionerReference")
    patient_reference: str = Field(..., alias="patientReference")
    start: str = Field(..., alias="start")
    end: str = Field(..., alias="end")
    priority: Optional[AppointmentPriority] = Field(
        AppointmentPriority.EMERGENCY, alias="priority"
    )
    organization_id: Optional[str] = Field(None, alias="organizationId")
    slot: Optional[str] = Field(None, alias="slot")
    reference: Optional[str] = Field(None, alias="reference")

    # @field_validator("practitioner_reference", "patient_reference", "start", "end")
    # @classmethod
    # def _validate_fields(cls, v: str, info: ValidationInfo) -> str:
    #     """Validates that required fields are not empty."""
    #     return check_not_empty(v, info.field_name)


class ResourceType(BaseModel):
    reference: str = Field(..., alias="reference")
    practitioner_reference: str = Field(..., alias="practitionerReference")
    patientReference: str = Field(..., alias="patientReference")
    slot: str = Field(..., alias="slot")
    priority: str = Field(..., alias="priority")
    start: str = Field(..., alias="start")
    end: str = Field(..., alias="end")
    organization_id: str = Field(..., alias="organizationId")


class CreateAppointmentResponeType(BaseModel):
    type: str
    message: str
    # resourceId: str
    validationErrors: Optional[list[Any]] = None
    resource: ResourceType
    fhirProfileId: Optional[str] = Field(default=None, exclude=True)

    class Config:
        orm_mode = True
