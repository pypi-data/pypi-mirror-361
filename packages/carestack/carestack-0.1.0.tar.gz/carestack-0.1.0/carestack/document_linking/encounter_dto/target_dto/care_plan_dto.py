from pydantic import BaseModel, Field, ValidationInfo, field_validator

from carestack.common.enums import CarePlanIntent, CarePlanStatus
from carestack.common.error_validation import check_not_empty
from carestack.document_linking.encounter_dto.target_dto.snomed_code_dto import (
    SnomedCode,
)


class CarePlan(BaseModel):
    """Represents a care plan."""

    category: SnomedCode = Field(..., alias="category")
    status: CarePlanStatus = Field(..., alias="status")
    intent: CarePlanIntent = Field(..., alias="intent")
    title: str = Field(..., alias="title")

    # @field_validator("category")
    # def _category_not_empty(cls, v: SnomedCode, info: ValidationInfo) -> SnomedCode:
    #     """Validates that the category is not empty."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("status")
    # def _status_not_empty(
    #     cls, v: CarePlanStatus, info: ValidationInfo
    # ) -> CarePlanStatus:
    #     """Validates that the status is not empty."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("intent")
    # def _intent_not_empty(
    #     cls, v: CarePlanIntent, info: ValidationInfo
    # ) -> CarePlanIntent:
    #     """Validates that the intent is not empty."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("title")
    # def _title_not_empty(cls, v: str, info: ValidationInfo) -> str:
    #     """Validates that the title is not empty."""
    #     return check_not_empty(v, info.field_name)
