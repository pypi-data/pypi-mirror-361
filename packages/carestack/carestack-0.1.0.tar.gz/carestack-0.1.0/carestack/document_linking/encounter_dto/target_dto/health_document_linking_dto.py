from typing import Optional, Union
from pydantic import BaseModel, Field, ValidationInfo, field_validator
import re

from carestack.common.enums import AppointmentPriority, HealthInformationTypes
from carestack.common.error_validation import check_not_empty
from carestack.document_linking.encounter_dto.target_dto.health_information_dto import (
    HealthInformationDTO,
)


class HealthDocumentLinkingDTO(BaseModel):
    """Represents data for linking health documents."""

    patient_reference: str = Field(..., alias="patientReference")
    practitioner_reference: str = Field(..., alias="practitionerReference")
    patient_address: str = Field(..., alias="patientAddress")
    patient_name: str = Field(..., alias="patientName")
    appointment_start_date: str = Field(..., alias="appointmentStartDate")
    appointment_end_date: str = Field(..., alias="appointmentEndDate")
    appointment_priority: Optional[AppointmentPriority] = Field(
        None, alias="appointmentPriority"
    )
    organization_id: str = Field(..., alias="organizationId")
    appointment_slot: Optional[str] = Field(None, alias="appointmentSlot")
    reference: Optional[str] = Field(None, alias="reference")
    patient_abha_address: Optional[str] = Field(None, alias="patientAbhaAddress")
    hi_type: HealthInformationTypes = Field(..., alias="hiType")
    mobile_number: str = Field(..., alias="mobileNumber")
    health_records: list[HealthInformationDTO] = Field(..., alias="healthRecords")

    # @field_validator("appointment_priority", mode="before")
    # @classmethod
    # def _validate_appointment_priority(
    #     cls, v: Optional[Union[str, AppointmentPriority]]
    # ) -> Optional[AppointmentPriority]:
    #     if v is None:
    #         return None
    #     if isinstance(v, AppointmentPriority):
    #         return v
    #     if isinstance(v, str):
    #         try:
    #             return AppointmentPriority[v.upper()]
    #         except KeyError:
    #             raise ValueError("Invalid appointment priority")
    #     raise TypeError("Invalid appointment priority type")

    # @field_validator(
    #     "patient_reference",
    #     "practitioner_reference",
    #     "appointment_start_date",
    #     "appointment_end_date",
    #     "organization_id",
    # )
    # @classmethod
    # def _validate_fields(cls, v: str, info: ValidationInfo) -> str:
    #     """Validates that the required fields are not empty."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("patient_address")
    # @classmethod
    # def _patient_address_min_length(cls, v: str, info: ValidationInfo) -> str:
    #     """Validates that the patient address has a minimum length of 5."""
    #     if len(v) < 5:
    #         raise ValueError("Invalid patient address length")
    #     return check_not_empty(v, info.field_name)

    # @field_validator("patient_name")
    # @classmethod
    # def _patient_name_validation(cls, v: str, info: ValidationInfo) -> str:
    #     """Validates that the patient name has a minimum length of 3 and contains only letters and spaces."""
    #     if len(v) < 3:
    #         raise ValueError("Invalid patient name length")
    #     if not v.replace(" ", "").isalpha():
    #         raise ValueError("Invalid patient name format")
    #     return check_not_empty(v, info.field_name)

    # @field_validator("patient_abha_address")
    # @classmethod
    # def _patient_abha_address_format(cls, v: Optional[str]) -> Optional[str]:
    #     """Validates that patient Abha Address  must match the format @(?:sbx|abdm)$"""
    #     if v is not None and not v.endswith(("@sbx", "@abdm")):
    #         raise ValueError("Invalid patient Abha Address format")
    #     return v

    # @field_validator("hi_type")
    # @classmethod
    # def _hi_type_not_empty(
    #     cls, v: HealthInformationTypes, info: ValidationInfo
    # ) -> HealthInformationTypes:
    #     """Validates that the HI type is not empty."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("mobile_number")
    # @classmethod
    # def _mobile_number_format(cls, v: str, info: ValidationInfo) -> str:
    #     """
    #     Validates that the mobile number is in the correct format (+[country code][number])
    #     and is not included '*' if mobileNumber not empty
    #     """
    #     if v and "*" not in v:
    #         if not re.fullmatch(r"^\+[0-9]{1,3}[0-9]{10,12}$", v):
    #             raise ValueError("Invalid mobile number format")
    #     return check_not_empty(v, info.field_name)

    # @field_validator("health_records")
    # @classmethod
    # def _health_records_not_empty(
    #     cls, v: list[HealthInformationDTO]
    # ) -> list[HealthInformationDTO]:
    #     """Validates that the health records list is not empty."""
    #     return check_not_empty(v, "health records list")
