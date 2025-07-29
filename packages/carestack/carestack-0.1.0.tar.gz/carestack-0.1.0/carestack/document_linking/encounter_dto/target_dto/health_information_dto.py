from typing import Optional, Any
from pydantic import BaseModel, Field, ValidationInfo, field_validator

from carestack.common.enums import HealthInformationTypes
from carestack.common.error_validation import check_not_empty


class HealthInformationDTO(BaseModel):
    """Represents health information data."""

    raw_fhir: Optional[bool] = Field(None, alias="rawFhir")
    fhir_document: Optional[dict] = Field(None, alias="fhirDocument")
    information_type: HealthInformationTypes = Field(..., alias="informationType")
    dto: dict[str, Any] = Field(..., alias="dto")

    # @field_validator("fhir_document")
    # @classmethod
    # def _fhir_document_validate_if_raw_fhir(
    #     cls, v: Optional[dict], info: ValidationInfo
    # ) -> Optional[dict]:
    #     """Validates that fhirDocument is provided if rawFhir is True."""
    #     if info.data.get("raw_fhir") and v is None:
    #         raise ValueError("fhirDocument must be provided when rawFhir is True")
    #     return v

    # @field_validator("dto", mode="before")
    # @classmethod
    # def _dto_validate(cls, v: dict[str, Any], info: ValidationInfo) -> dict[str, Any]:
    #     """
    #     Validates and potentially transforms the 'dto' dictionary based on the
    #     'raw_fhir' and 'fhir_document' fields.

    #     Args:
    #         v: The 'dto' value (a dictionary).
    #         info: ValidationInfo containing context about the validation process.

    #     Returns:
    #         The validated or transformed 'dto' dictionary.

    #     Raises:
    #         ValueError: If 'raw_fhir' is False, 'fhir_document' is None, and the
    #                     'dto' content is not recognized or invalid.
    #     """
    #     if not info.data.get("raw_fhir") and not info.data.get("fhir_document"):
    #         # Check if v is a dictionary
    #         if not isinstance(v, dict):
    #             raise ValueError("Invalid dto content: dto must be a dictionary")

    #         if any(
    #             key in v
    #             for key in [
    #                 "medications",
    #                 "conditions",
    #                 "procedures",
    #                 "carePlans",
    #                 "advisoryNotes",
    #                 "medicalHistory",
    #                 "familyHistory",
    #                 "allergies",
    #                 "physicalExamination",
    #                 "followUps",
    #                 "opConsultDocuments",
    #                 "investigationAdvice",
    #                 "dischargeSummaryDocuments",
    #                 "healthDocuments",
    #                 "prescriptionBinaries",
    #                 "wellnessDocuments",
    #                 "immunizations",
    #                 "reports",
    #             ]
    #         ):
    #             return v
    #         raise ValueError("Invalid dto content: does not match any known structure")
    #     return v

    # @field_validator("information_type")
    # @classmethod
    # def _information_type_not_empty(
    #     cls,
    #     v: HealthInformationTypes,
    #     info: ValidationInfo,
    # ) -> HealthInformationTypes:
    #     """Validates that the information type is not empty."""
    #     return check_not_empty(v, info.field_name)
