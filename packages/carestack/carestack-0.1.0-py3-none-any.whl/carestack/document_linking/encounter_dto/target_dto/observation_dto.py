from typing import Optional
from pydantic import Field, ValidationInfo, field_validator

from carestack.common.enums import ObservationStatus
from carestack.common.error_validation import check_not_empty
from carestack.document_linking.encounter_dto.target_dto.reference_range_dto import (
    ReferenceRange,
)
from carestack.document_linking.encounter_dto.target_dto.snomed_code_dto import (
    SnomedCode,
)
from carestack.document_linking.encounter_dto.target_dto.value_quantity_dto import (
    ValueQuantity,
)


class Observation(SnomedCode):
    """Represents an observation."""

    status: ObservationStatus = Field(..., alias="status")
    effective_date_time: Optional[str] = Field(None, alias="effectiveDateTime")
    value_quantity: ValueQuantity = Field(alias="valueQuantity")
    reference_range: ReferenceRange = Field(alias="referenceRange")

    # @field_validator("status")
    # @classmethod
    # def _status_not_empty(
    #     cls,
    #     v: ObservationStatus,
    #     info: ValidationInfo,
    # ) -> ObservationStatus:
    #     """Validates that the status is not empty."""
    #     return check_not_empty(v, info.field_name)
