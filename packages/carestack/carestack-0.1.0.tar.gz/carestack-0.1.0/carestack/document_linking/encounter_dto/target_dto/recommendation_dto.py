from typing import Optional
from pydantic import BaseModel, Field

from carestack.document_linking.encounter_dto.target_dto.generic_dto import (
    GenericCode,
)


class RecommendationDTO(BaseModel):
    """Represents a recommendation, potentially for a vaccine."""

    vaccine_code: Optional[GenericCode] = Field(None, alias="vaccineCode")
    target_disease: Optional[GenericCode] = Field(None, alias="targetDisease")
    contraindicated_vaccine_code: Optional[GenericCode] = Field(
        None, alias="contraindicatedVaccineCode"
    )
    forecast_status: Optional[GenericCode] = Field(None, alias="forecastStatus")
    forecast_reason: Optional[GenericCode] = Field(None, alias="forecastReason")
    date_criterion: Optional[GenericCode] = Field(None, alias="dateCriterion")
