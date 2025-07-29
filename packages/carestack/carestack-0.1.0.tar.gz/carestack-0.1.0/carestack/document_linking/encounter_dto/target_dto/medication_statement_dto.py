from typing import Optional
from pydantic import Field

from carestack.common.enums import MedicationStatementStatus
from carestack.document_linking.encounter_dto.target_dto.snomed_code_dto import (
    SnomedCode,
)


class MedicationStatement(SnomedCode):
    """Represents a medication statement."""

    status: Optional[MedicationStatementStatus] = Field(None, alias="status")
    date_asserted: Optional[str] = Field(None, alias="dateAsserted")
    reason_code: SnomedCode = Field(alias="reasonCode")
    medication: SnomedCode = Field(alias="medication")
