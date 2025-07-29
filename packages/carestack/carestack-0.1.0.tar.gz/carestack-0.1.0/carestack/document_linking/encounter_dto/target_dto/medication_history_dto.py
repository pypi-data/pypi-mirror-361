from pydantic import BaseModel, Field, field_validator

from carestack.common.error_validation import check_not_empty
from carestack.document_linking.encounter_dto.target_dto.procedure_dto import (
    Procedure,
)
from carestack.document_linking.encounter_dto.target_dto.condition_dto import (
    Condition,
)


class MedicationHistory(BaseModel):
    """Represents a patient's medical history."""

    conditions: list[Condition] = Field(...)
    procedures: list[Procedure] = Field(...)

    # @field_validator("conditions")
    # @classmethod
    # def _conditions_not_empty(cls, v: list[Condition]) -> list[Condition]:
    #     """Validates that the conditions list is not empty."""
    #     return check_not_empty(v, "conditions list")

    # @field_validator("procedures")
    # @classmethod
    # def _procedures_not_empty(cls, v: list[Procedure]) -> list[Procedure]:
    #     """Validates that the procedures list is not empty."""
    #     return check_not_empty(v, "procedures list")
