from typing import Optional
from pydantic import Field

from carestack.common.enums import ServiceRequestIntent, ServiceRequestStatus
from carestack.document_linking.encounter_dto.target_dto.snomed_code_dto import (
    SnomedCode,
)


class ServiceRequest(SnomedCode):
    """Represents a service request."""

    status: Optional[ServiceRequestIntent] = Field(None)
    """The status of the service request (e.g., PROPOSAL, PLAN, ORDER)."""

    intent: Optional[ServiceRequestStatus] = Field(None)
    """The intent of the service request (e.g., DRAFT, ACTIVE, COMPLETED)."""
