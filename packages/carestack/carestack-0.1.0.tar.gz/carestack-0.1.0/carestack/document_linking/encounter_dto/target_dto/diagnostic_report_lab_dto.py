from typing import Optional
from pydantic import Field

from carestack.document_linking.encounter_dto.target_dto.diagnostic_report_dto import (
    DiagnosticReport,
)
from carestack.document_linking.encounter_dto.target_dto.observation_dto import (
    Observation,
)


class DiagnosticReportLab(DiagnosticReport):
    """Represents a diagnostic report with lab observations."""

    observations: Optional[list[Observation]] = Field(None)
