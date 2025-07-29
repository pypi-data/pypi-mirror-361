from typing import Optional
from pydantic import BaseModel, Field

from carestack.common.enums import (
    DosageFrequency,
    MedicationMethod,
    MedicationRoute,
)


class DosageInstruction(BaseModel):
    """Represents dosage instructions for a medication."""

    duration: Optional[int] = Field(None, alias="duration")
    frequency: Optional[DosageFrequency] = Field(None, alias="frequency")
    route: Optional[MedicationRoute] = Field(None, alias="route")
    method: Optional[MedicationMethod] = Field(None, alias="method")
