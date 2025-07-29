from pydantic import Field, ValidationInfo, field_validator

from carestack.common.enums import ProcedureStatus
from carestack.common.error_validation import check_not_empty
from carestack.document_linking.encounter_dto.target_dto.snomed_code_dto import (
    SnomedCode,
)


class Procedure(SnomedCode):
    """Represents a medical procedure."""

    status: ProcedureStatus = Field(..., alias="status")
    procedure: SnomedCode = Field(..., alias="procedure")
    complications: SnomedCode = Field(..., alias="complications")
    performed_date: str = Field(..., alias="performedDate")

    # @field_validator("status")
    # @classmethod
    # def _status_not_empty(
    #     cls, v: ProcedureStatus, info: ValidationInfo
    # ) -> ProcedureStatus:
    #     """Validates that the status is not empty."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("procedure", "complications")
    # @classmethod
    # def _validate_fields(cls, v: SnomedCode, info: ValidationInfo) -> SnomedCode:
    #     """Validates that required fields are not empty."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("performed_date")
    # @classmethod
    # def _performed_date_not_empty(cls, v: str, info: ValidationInfo) -> str:
    #     """Validates that the performed date is not empty."""
    #     return check_not_empty(v, info.field_name)
