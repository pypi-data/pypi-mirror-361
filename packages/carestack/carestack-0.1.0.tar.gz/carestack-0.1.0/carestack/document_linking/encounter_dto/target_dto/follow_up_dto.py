from typing import Union
from pydantic import BaseModel, Field, ValidationInfo, field_validator

from carestack.common.error_validation import check_not_empty
from carestack.document_linking.encounter_dto.target_dto.snomed_code_dto import (
    SnomedCode,
)


class FollowUp(BaseModel):
    """Represents follow-up information."""

    service_category: SnomedCode = Field(..., alias="serviceCategory")
    service_type: SnomedCode = Field(..., alias="serviceType")
    appointment_type: SnomedCode = Field(..., alias="appointmentType")
    appointment_reference: str = Field(..., alias="appointmentReference")

    # @field_validator(
    #     "service_category", "service_type", "appointment_type", "appointment_reference"
    # )
    # @classmethod
    # def _validate_fields(
    #     cls, v: Union[SnomedCode, str], info: ValidationInfo
    # ) -> Union[SnomedCode, str]:
    #     """Validates that required fields are not empty."""
    #     return check_not_empty(v, info.field_name)
