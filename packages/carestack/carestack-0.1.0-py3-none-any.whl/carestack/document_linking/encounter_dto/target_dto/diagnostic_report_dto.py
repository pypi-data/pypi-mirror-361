from pydantic import Field, ValidationInfo, field_validator

from carestack.common.enums import DiagnosticReportStatus
from carestack.common.error_validation import check_not_empty
from carestack.document_linking.encounter_dto.target_dto.snomed_code_dto import (
    SnomedCode,
)


class DiagnosticReport(SnomedCode):
    """Represents a diagnostic report."""

    status: DiagnosticReportStatus = Field(..., alias="status")
    category: SnomedCode = Field(..., alias="category")
    conclusion: str = Field(..., alias="conclusion")
    conclusion_code: SnomedCode = Field(..., alias="conclusionCode")
    recorded_date: str = Field(..., alias="recordedDate")

    # @field_validator("status")
    # @classmethod
    # def _status_not_empty(
    #     cls, v: DiagnosticReportStatus, info: ValidationInfo
    # ) -> DiagnosticReportStatus:
    #     """Validates that the status is not empty."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("category", "conclusion_code")
    # @classmethod
    # def _validate_fields(cls, v: SnomedCode, info: ValidationInfo) -> SnomedCode:
    #     """Validates that required fields are not empty."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("conclusion", "recorded_date")
    # @classmethod
    # def _validate_not_empty(cls, v: str, info: ValidationInfo) -> str:
    #     """Validates that required fields are not empty."""
    #     return check_not_empty(v, info.field_name)
