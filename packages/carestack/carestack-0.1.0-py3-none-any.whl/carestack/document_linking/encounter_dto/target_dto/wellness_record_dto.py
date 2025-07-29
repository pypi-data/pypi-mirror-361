from typing import Optional
from pydantic import BaseModel, Field, field_validator

from carestack.common.error_validation import check_not_empty
from carestack.document_linking.encounter_dto.target_dto.document_reference_dto import (
    DocumentReference,
)
from carestack.document_linking.encounter_dto.target_dto.observation_dto import (
    Observation,
)


class WellnessRecordDTO(BaseModel):
    """Represents a wellness record."""

    vital_signs: Optional[list[Observation]] = Field(None, alias="vitalSigns")
    body_measurements: Optional[list[Observation]] = Field(
        None, alias="bodyMeasurements"
    )
    physical_activities: Optional[list[Observation]] = Field(
        None, alias="physicalActivities"
    )
    general_assessments: Optional[list[Observation]] = Field(
        None, alias="generalAssessments"
    )
    women_health: Optional[list[Observation]] = Field(None, alias="womenHealth")
    life_style: Optional[list[Observation]] = Field(None, alias="lifeStyle")
    others: Optional[list[Observation]] = Field(None, alias="others")
    wellness_documents: list[DocumentReference] = Field(..., alias="wellnessDocuments")

    # @field_validator("wellness_documents")
    # @classmethod
    # def _wellness_documents_not_empty(
    #     cls, v: list[DocumentReference]
    # ) -> list[DocumentReference]:
    #     """Validates that the wellness documents list is not empty."""
    #     return check_not_empty(v, "wellness documents list")
