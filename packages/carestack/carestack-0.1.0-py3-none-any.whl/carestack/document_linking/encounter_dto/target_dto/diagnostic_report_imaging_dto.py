from pydantic import Field, ValidationInfo, field_validator

from carestack.common.error_validation import check_not_empty
from carestack.document_linking.encounter_dto.target_dto.diagnostic_report_dto import (
    DiagnosticReport,
)
from carestack.document_linking.encounter_dto.target_dto.document_reference_dto import (
    DocumentReference,
)


class DiagnosticReportImaging(DiagnosticReport):
    """Represents a diagnostic report with imaging information."""

    imaging: DocumentReference = Field(..., alias="imaging")

    # @field_validator("imaging")
    # @classmethod
    # def _validate_imaging(
    #     cls,
    #     v: DocumentReference,
    #     info: ValidationInfo,
    # ) -> DocumentReference:
    #     """Validates that the imaging field is not empty."""
    #     return check_not_empty(v, info.field_name)
