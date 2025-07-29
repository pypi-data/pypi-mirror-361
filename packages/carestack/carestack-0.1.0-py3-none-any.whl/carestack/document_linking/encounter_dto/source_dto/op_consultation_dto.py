from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from carestack.common.error_validation import check_not_empty


class VitalSign(BaseModel):
    value: str = Field(..., description="The value of the vital sign.")
    unit: str = Field(..., description="The unit of the vital sign.")

    @field_validator("value", "unit")
    @classmethod
    def _validate_fields(cls, v: str, info: ValidationInfo) -> str:
        """Validates that required fields are not empty."""
        return check_not_empty(v, info.field_name)


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


class MedicalHistoryItem(BaseModel):
    condition: Optional[str] = Field(
        None, description="A medical condition in the patient's history."
    )
    procedure: Optional[str] = Field(
        None, description="A medical procedure in the patient's history."
    )

    @field_validator("condition")
    @classmethod
    def _validate_condition(
        cls, v: Optional[str], info: ValidationInfo
    ) -> Optional[str]:
        """Validates that condition is not empty if provided."""
        if v is not None:
            return check_not_empty(v, info.field_name)
        return v

    @field_validator("procedure")
    @classmethod
    def _validate_procedure(
        cls, v: Optional[str], info: ValidationInfo
    ) -> Optional[str]:
        """Validates that procedure is not empty if provided."""
        if v is not None:
            return check_not_empty(v, info.field_name)
        return v


class FamilyHistoryItem(BaseModel):
    relation: str = Field(..., description="The relation to the patient.")
    condition: str = Field(..., description="The medical condition of the relative.")

    @field_validator("relation", "condition")
    @classmethod
    def _validate_fields(cls, v: str, info: ValidationInfo) -> str:
        """Validates that required fields are not empty."""
        return check_not_empty(v, info.field_name)


class ProcedureItem(BaseModel):
    description: str = Field(..., description="Description of the procedure.")
    complications: Optional[str] = Field(
        None, description="Any complications during the procedure."
    )

    @field_validator("description")
    @classmethod
    def _validate_description(cls, v: str, info: ValidationInfo) -> str:
        """Validates that required fields are not empty."""
        return check_not_empty(v, info.field_name)

    @field_validator("complications")
    @classmethod
    def _validate_complications(
        cls, v: Optional[str], info: ValidationInfo
    ) -> Optional[str]:
        """Validates that complications is not empty if provided."""
        if v is not None:
            return check_not_empty(v, info.field_name)
        return v


class OpConsultationDTO(BaseModel):
    chief_complaints: str = Field(
        ..., alias="chiefComplaints", description="The patient's chief complaints."
    )
    physical_examination: PhysicalExamination = Field(
        ...,
        alias="physicalExamination",
        description="Results of the physical examination.",
    )
    medical_history: List[MedicalHistoryItem] = Field(
        ..., alias="medicalHistory", description="The patient's medical history."
    )
    family_history: List[FamilyHistoryItem] = Field(
        ..., alias="familyHistory", description="The patient's family medical history."
    )
    allergies: List[str] = Field(..., description="The patient's known allergies.")
    immunizations: List[str] = Field(..., description="The patient's immunizations.")
    current_medications: List[str] = Field(
        ...,
        alias="currentMedications",
        description="The patient's current medications.",
    )
    conditions: List[str] = Field(..., description="The patient's current conditions.")
    investigation_advice: List[str] = Field(
        ...,
        alias="investigationAdvice",
        description="Advice on further investigations.",
    )
    prescribed_medications: List[str] = Field(
        ...,
        alias="prescribedMedications",
        description="Medications prescribed to the patient.",
    )
    current_procedures: List[ProcedureItem] = Field(
        ...,
        alias="currentProcedures",
        description="Procedures currently being performed on the patient.",
    )
    advisory_notes: List[str] = Field(
        ..., alias="advisoryNotes", description="Advisory notes for the patient."
    )
    follow_up: List[str] = Field(
        ..., alias="followUp", description="Follow-up instructions."
    )
    op_consult_document: List[str] = Field(
        ...,
        alias="opConsultDocument",
        description="Documents related to the outpatient consultation.",
    )

    @field_validator(
        "chief_complaints",
        "allergies",
        "immunizations",
        "conditions",
        "investigation_advice",
        "prescribed_medications",
        "advisory_notes",
        "follow_up",
        "op_consult_document",
    )
    @classmethod
    def _validate_list_fields(
        cls, v: Union[str, List[str]], info: ValidationInfo
    ) -> Union[str, List[str]]:
        """Validates that required fields are not empty."""
        if isinstance(v, str):
            return check_not_empty(v, info.field_name)
        if isinstance(v, list):
            if info.field_name != "op_consult_document":
                if not v:
                    raise ValueError(f"{info.field_name} cannot be an empty list")
            for item in v:
                check_not_empty(item, info.field_name)
            return v
        raise ValueError(f"Invalid type for {info.field_name}")

    @field_validator("medical_history")
    @classmethod
    def _validate_medical_history(
        cls, v: List[MedicalHistoryItem], info: ValidationInfo
    ) -> List[MedicalHistoryItem]:
        """Validates that medicalHistory is not an empty list."""
        if not v:
            raise ValueError(f"{info.field_name} cannot be an empty list")
        return v

    @field_validator("family_history")
    @classmethod
    def _validate_family_history(
        cls, v: List[FamilyHistoryItem], info: ValidationInfo
    ) -> List[FamilyHistoryItem]:
        """Validates that familyHistory is not an empty list."""
        if not v:
            raise ValueError(f"{info.field_name} cannot be an empty list")
        return v

    @field_validator("current_procedures")
    @classmethod
    def _validate_current_procedures(
        cls, v: List[ProcedureItem], info: ValidationInfo
    ) -> List[ProcedureItem]:
        """Validates that currentProcedures is not an empty list."""
        if not v:
            raise ValueError(f"{info.field_name} cannot be an empty list")
        return v
