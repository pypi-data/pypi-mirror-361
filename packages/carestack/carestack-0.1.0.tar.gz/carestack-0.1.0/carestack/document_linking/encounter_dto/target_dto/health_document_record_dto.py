from pydantic import BaseModel, Field, field_validator

from carestack.common.error_validation import check_not_empty
from carestack.document_linking.encounter_dto.target_dto.document_reference_dto import (
    DocumentReference,
)


class HealthDocumentRecordDTO(BaseModel):
    """Represents a record of health documents."""

    health_documents: list[DocumentReference] = Field(..., alias="healthDocuments")

    # @field_validator("health_documents")
    # @classmethod
    # def _health_documents_not_empty(
    #     cls, v: list[DocumentReference]
    # ) -> list[DocumentReference]:
    #     """Validates that the health documents list is not empty."""
    #     return check_not_empty(v, "health documents list")
