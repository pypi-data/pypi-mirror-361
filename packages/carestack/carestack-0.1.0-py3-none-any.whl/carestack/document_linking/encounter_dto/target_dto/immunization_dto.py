from typing import Optional
from pydantic import BaseModel, Field

from carestack.common.enums import ImmunizationStatusEnum
from carestack.document_linking.encounter_dto.target_dto.generic_dto import (
    GenericCode,
)


class Immunization(BaseModel):
    """Represents immunization information."""

    status: Optional[ImmunizationStatusEnum] = Field(None, alias="status")
    brand_name: Optional[str] = Field(None, alias="brandName")
    vaccine_code: Optional[GenericCode] = Field(None, alias="vaccineCode")
    occurrence_date_time: Optional[str] = Field(None, alias="occurrenceDateTime")
    lot_number: Optional[str] = Field(None, alias="lotNumber")
    expiration_date: Optional[str] = Field(None, alias="expirationDate")
