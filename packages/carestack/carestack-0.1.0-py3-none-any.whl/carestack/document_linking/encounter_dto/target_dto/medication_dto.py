from typing import Optional
from pydantic import BaseModel, Field

from carestack.document_linking.encounter_dto.target_dto.medication_request_dto import (
    MedicationRequest,
)
from carestack.document_linking.encounter_dto.target_dto.medication_statement_dto import (
    MedicationStatement,
)


class Medication(BaseModel):
    """Represents medication information, including statements and requests."""

    statement: Optional[list[MedicationStatement]] = Field(None)
    request: Optional[list[MedicationRequest]] = Field(None)
