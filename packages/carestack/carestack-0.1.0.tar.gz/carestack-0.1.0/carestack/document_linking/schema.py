from datetime import datetime

from carestack.common.enums import AppointmentPriority, AuthMode
from carestack.document_linking.encounter_dto.target_dto.appointment_dto import (
    AppointmentDTO,
)
from carestack.document_linking.encounter_dto.target_dto.create_care_context_dto import (
    CreateCareContextDTO,
)
from carestack.document_linking.encounter_dto.target_dto.health_document_linking_dto import (
    HealthDocumentLinkingDTO,
)
from carestack.document_linking.encounter_dto.target_dto.link_care_context_dto import (
    LinkCareContextDTO,
)
from carestack.document_linking.encounter_dto.target_dto.update_visit_records_dto import (
    UpdateVisitRecordsDTO,
)


def map_to_appointment_dto(data: HealthDocumentLinkingDTO) -> AppointmentDTO:
    """Maps HealthDocumentLinkingDTO to AppointmentDTO."""
    priority = (
        data.appointment_priority
        if data.appointment_priority is not None
        else AppointmentPriority.EMERGENCY
    )
    return AppointmentDTO(
        practitionerReference=data.practitioner_reference,
        patientReference=data.patient_reference,
        start=data.appointment_start_date,
        end=data.appointment_end_date,
        priority=priority,
        organizationId=data.organization_id,
        slot=data.appointment_slot,
        reference=data.reference,
    )


def format_appointment_date(start_date: str, end_date: str) -> str:
    """Formats appointment start and end dates to 'hh:mm a - hh:mm a'."""
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)

    def format_time(date):
        return date.strftime("%I:%M %p").lower()

    return f"{format_time(start)} - {format_time(end)}"


def map_to_create_care_context_dto(
    data: HealthDocumentLinkingDTO,
    appointment_reference: str,
    appointment_start_date: str,
    appointment_end_date: str,
) -> CreateCareContextDTO:
    """Maps HealthDocumentLinkingDTO to CreateCareContextDTO."""

    appointment_date = format_appointment_date(
        appointment_start_date, appointment_end_date
    )
    return CreateCareContextDTO(
        patientReference=data.patient_reference,
        patientAbhaAddress=data.patient_abha_address,
        practitionerReference=data.practitioner_reference,
        appointmentReference=appointment_reference,
        hiType=data.hi_type,
        appointmentDate=appointment_date,
        resendOtp=False,
    )


def map_to_consultation_dto(
    data: HealthDocumentLinkingDTO,
    care_context_reference: str,
    appointment_reference: str,
    request_id: str,
) -> UpdateVisitRecordsDTO:
    """Maps HealthDocumentLinkingDTO to UpdateVisitRecordsDTO."""

    return UpdateVisitRecordsDTO(
        careContextReference=care_context_reference,
        patientReference=data.patient_reference,
        practitionerReference=data.practitioner_reference,
        appointmentReference=appointment_reference,
        patientAbhaAddress=data.patient_abha_address,
        healthRecords=data.health_records or [],
        mobileNumber=data.mobile_number,
        requestId=request_id,
    )


def map_to_link_care_context_dto(
    data: HealthDocumentLinkingDTO,
    care_context_reference: str,
    appointment_reference: str,
    request_id: str,
) -> LinkCareContextDTO:
    """Maps HealthDocumentLinkingDTO to LinkCareContextDTO."""

    return LinkCareContextDTO(
        requestId=request_id or "",
        appointmentReference=appointment_reference,
        patientAddress=data.patient_address,
        patientName=data.patient_name,
        patientReference=data.patient_reference,
        careContextReference=care_context_reference,
        authMode=AuthMode.DEMOGRAPHICS,
    )
