from typing import Optional
from pydantic import BaseModel, Field

from carestack.document_linking.encounter_dto.target_dto.recommendation_dto import (
    RecommendationDTO,
)


class ImmunizationRecommendation(BaseModel):
    """Represents an immunization recommendation."""

    recommendation: Optional[RecommendationDTO] = Field(None, alias="recommendation")
