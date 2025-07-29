from typing import Optional
from pydantic import BaseModel, Field, ValidationInfo, field_validator
from carestack.common.error_validation import check_not_empty


class ValueQuantity(BaseModel):
    value: Optional[str] = Field(None)
    unit: Optional[str] = Field(None)
    code: Optional[str] = Field(None)


class SnomedCode(BaseModel):
    """Represents a SNOMED code."""

    code: Optional[str] = Field(None, description="The SNOMED code.")
    text: Optional[str] = Field(None, description="The text description.")


class VitalSign(BaseModel):
    value: str = Field(..., description="The value of the vital sign.")
    unit: str = Field(..., description="The unit of the vital sign.")


class PhysicalExamination(BaseModel):
    blood_pressure: VitalSign = Field(
        ..., alias="bloodPressure", description="Blood pressure reading."
    )
    heart_rate: VitalSign = Field(
        ..., alias="heartRate", description="Heart rate reading."
    )
    respiratory_rate: VitalSign = Field(
        ..., alias="respiratoryRate", description="Respiratory rate reading."
    )
    temperature: VitalSign = Field(..., description="Temperature reading.")
    oxygen_saturation: VitalSign = Field(
        ..., alias="oxygenSaturation", description="Oxygen saturation reading."
    )
    height: VitalSign = Field(..., description="Height measurement.")
    weight: VitalSign = Field(..., description="Weight measurement.")


class ConditionItem(BaseModel):
    description: str = Field(..., description="Description of the condition.")
    status: str = Field(..., description="Status of the condition.")


class FamilyHistoryItem(BaseModel):
    relation: str = Field(..., description="The relation to the patient.")
    health_note: str = Field(
        ..., alias="healthNote", description="The medical condition of the relative."
    )
    status: str = Field(..., description="Status of the family history item.")


class AllergyItem(BaseModel):
    status: str = Field(..., description="Status of the allergy.")
    verification_status: str = Field(
        ...,
        alias="verificationStatus",
        description="Verification status of the allergy.",
    )
    recorded_date: str = Field(
        ..., alias="recordedDate", description="Date the allergy was recorded."
    )
    reaction: str = Field(..., description="Reaction to the allergen.")


class ImmunizationItem(BaseModel):
    status: str = Field(..., description="Status of the immunization.")
    brand_name: str = Field(
        ..., alias="brandName", description="Brand name of the vaccine."
    )
    vaccine_name: str = Field(
        ..., alias="vaccineName", description="Name of the vaccine."
    )
    vaccinated_date: str = Field(
        ..., alias="vaccinatedDate", description="Date of vaccination."
    )
    lot_number: str = Field(
        ..., alias="lotNumber", description="Lot number of the vaccine."
    )
    expiration_date: str = Field(
        ..., alias="expirationDate", description="Expiration date of the vaccine."
    )


class CurrentMedicationItem(BaseModel):
    status: str = Field(..., description="Status of the medication.")
    date_asserted: Optional[str] = Field(
        ..., alias="dateAsserted", description="Date the medication was asserted."
    )
    medication: str = Field(..., description="Name of the medication.")
    reason: str = Field(..., description="Reason for the medication.")


class InvestigationAdviceItem(BaseModel):
    description: str = Field(..., description="Description of the investigation.")
    status: str = Field(..., description="Status of the investigation.")
    intent: str = Field(..., description="Intent of the investigation.")


class PrescribedMedicationItem(BaseModel):
    status: str = Field(..., description="Status of the prescribed medication.")
    authored_on: str = Field(
        ..., alias="authoredOn", description="Date the medication was prescribed."
    )
    dosage_duration: int = Field(
        ..., alias="dosageDuration", description="Duration of the dosage."
    )
    dosage_frequency: str = Field(
        ..., alias="dosageFrequency", description="Frequency of the dosage."
    )
    medication_route: str = Field(
        ..., alias="medicationRoute", description="Route of medication administration."
    )
    medication_method: str = Field(
        ...,
        alias="medicationMethod",
        description="Method of medication administration.",
    )
    medication: str = Field(..., description="Name of the medication.")
    reason: str = Field(..., description="Reason for the medication.")


class ProcedureItem(BaseModel):
    status: str = Field(..., description="Status of the procedure.")
    procedure_text: str = Field(
        ..., alias="procedureText", description="Description of the procedure."
    )
    complication_text: str = Field(
        ...,
        alias="complicationText",
        description="Any complications during the procedure.",
    )
    performed_date: str = Field(
        ..., alias="performedDate", description="Date of the procedure."
    )


class AdvisoryNoteItem(BaseModel):
    category: str = Field(description="Category of the advisory note.")
    note: str = Field(..., description="Content of the advisory note.")


class FollowUpItem(BaseModel):
    service_category: str = Field(
        ..., alias="serviceCategory", description="Category of the follow-up service."
    )
    service_type: str = Field(
        ..., alias="serviceType", description="Type of the follow-up service."
    )
    appointment_type: str = Field(
        ..., alias="appointmentType", description="Type of the follow-up appointment."
    )
    appointment_reference: str = Field(
        ...,
        alias="appointmentReference",
        description="Reference for the follow-up appointment.",
    )


class DocumentReferenceItem(BaseModel):
    base64_file: str = Field(
        ..., alias="base64File", description="Base64 encoded file content."
    )


class CarePlanItem(BaseModel):
    status: str = Field(..., description="Status of the care plan.")
    intent: str = Field(..., description="Intent of the care plan.")
    title: str = Field(..., description="Title of the care plan.")
    description: str = Field(..., description="Description of the care plan.")


class DischargeSummaryDocumentItem(BaseModel):
    base64_file: str = Field(
        ..., alias="base64File", description="Base64 encoded file content."
    )


class ObservationItem(BaseModel):
    """Represents a single observation in the intermediate stage."""

    text: Optional[str] = Field(
        None, description="Name or description of the observation/test."
    )
    status: Optional[str] = Field(
        None, description="Status string (e.g., 'final', 'preliminary', 'registered')."
    )
    effective_date_time: Optional[str] = Field(
        None,
        alias="effectiveDateTime",
        description="Date/time string of the observation.",
    )
    value: Optional[str] = Field(None, description="The observed value as a string.")
    unit: Optional[str] = Field(None, description="The unit for the value as a string.")


class DiagnosticReportLabItem(BaseModel):
    observations: Optional[list[ObservationItem]] = Field(None, alias="observations")


class DiagnosticReportImagingItem(BaseModel):
    data: str = Field(..., alias="data")
