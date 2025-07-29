from typing import Optional, Union
from pydantic import BaseModel, Field, ValidationInfo, field_validator

from carestack.common.error_validation import check_not_empty
from carestack.document_linking.encounter_dto.target_dto.allergy_intolerance_dto import (
    AllergyIntolerance,
)
from carestack.document_linking.encounter_dto.target_dto.care_plan_dto import (
    CarePlan,
)
from carestack.document_linking.encounter_dto.target_dto.diagnostic_report_imaging_dto import (
    DiagnosticReportImaging,
)
from carestack.document_linking.encounter_dto.target_dto.diagnostic_report_lab_dto import (
    DiagnosticReportLab,
)
from carestack.document_linking.encounter_dto.target_dto.document_reference_dto import (
    DocumentReference,
)
from carestack.document_linking.encounter_dto.target_dto.medication_history_dto import (
    MedicationHistory,
)
from carestack.document_linking.encounter_dto.target_dto.medication_request_dto import (
    MedicationRequest,
)
from carestack.document_linking.encounter_dto.target_dto.medication_statement_dto import (
    MedicationStatement,
)
from carestack.document_linking.encounter_dto.target_dto.observation_dto import (
    Observation,
)
from carestack.document_linking.encounter_dto.target_dto.procedure_dto import (
    Procedure,
)
from carestack.document_linking.encounter_dto.target_dto.condition_dto import (
    Condition,
)


def transform_to_condition_or_procedure(obj: dict) -> Union[Condition, Procedure]:
    """Transforms a dictionary to a Condition or Procedure object."""
    if "procedure" in obj:
        return Procedure(**obj)
    return Condition(**obj)


def transform_to_diagnostic_report(
    obj: dict,
) -> Union[DiagnosticReportLab, DiagnosticReportImaging]:
    """Transforms a dictionary to a DiagnosticReportLab or DiagnosticReportImaging object."""
    if "imaging" in obj:
        return DiagnosticReportImaging(**obj)
    return DiagnosticReportLab(**obj)


class DischargeSummaryRecordDTO(BaseModel):
    """Represents a discharge summary record."""

    conditions: Optional[list[Condition]] = Field(None, alias="conditions")
    discharge_summary_documents: list[DocumentReference] = Field(
        ..., alias="dischargeSummaryDocuments"
    )
    medical_history: Optional[list[Union[Condition, Procedure]]] = Field(
        None, alias="medicalHistory"
    )
    family_history: Optional[MedicationHistory] = Field(None, alias="familyHistory")
    investigations: Optional[
        list[Union[DiagnosticReportLab, DiagnosticReportImaging]]
    ] = Field(None, alias="investigations")
    procedures: Optional[list[Procedure]] = Field(None, alias="procedures")
    medications: Optional[list[MedicationRequest]] = Field(None, alias="medications")
    care_plan: Optional[list[CarePlan]] = Field(None, alias="carePlan")
    physical_examination: Optional[list[Observation]] = Field(
        None, alias="physicalExamination"
    )
    allergies: Optional[list[AllergyIntolerance]] = Field(None, alias="allergies")
    medication_statements: Optional[list[MedicationStatement]] = Field(
        None, alias="medicationStatements"
    )

    # @field_validator("conditions")
    # @classmethod
    # def _conditions_not_empty(
    #     cls, v: Optional[list[Condition]], info: ValidationInfo
    # ) -> Optional[list[Condition]]:
    #     """Validates that conditions is not an empty list if provided."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("discharge_summary_documents")
    # @classmethod
    # def _discharge_summary_documents_not_empty(
    #     cls, v: list[DocumentReference], info: ValidationInfo
    # ) -> list[DocumentReference]:
    #     """Validates that discharge_summary_documents is not an empty list."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("medical_history")
    # @classmethod
    # def _medical_history_transform(
    #     cls, v: Optional[list[dict]]
    # ) -> Optional[list[Union[Condition, Procedure]]]:
    #     """Transforms and validates the medical history list."""
    #     if v is None:
    #         return None
    #     if not v:
    #         raise ValueError("medicalHistory cannot be an empty array if provided")
    #     return [transform_to_condition_or_procedure(item) for item in v]

    # @field_validator("investigations")
    # @classmethod
    # def _investigations_transform(
    #     cls, v: Optional[list[dict]]
    # ) -> Optional[list[Union[DiagnosticReportLab, DiagnosticReportImaging]]]:
    #     """Transforms and validates the investigations list."""
    #     if v is None:
    #         return None
    #     if not v:
    #         raise ValueError("investigations cannot be an empty array if provided")
    #     return [transform_to_diagnostic_report(item) for item in v]

    # @field_validator("procedures")
    # @classmethod
    # def _procedures_not_empty(
    #     cls, v: Optional[list[Procedure]], info: ValidationInfo
    # ) -> Optional[list[Procedure]]:
    #     """Validates that procedures is not an empty list if provided."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("medications")
    # @classmethod
    # def _medications_not_empty(
    #     cls, v: Optional[list[MedicationRequest]], info: ValidationInfo
    # ) -> Optional[list[MedicationRequest]]:
    #     """Validates that medications is not an empty list if provided."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("care_plan")
    # @classmethod
    # def _care_plan_not_empty(
    #     cls, v: Optional[list[CarePlan]], info: ValidationInfo
    # ) -> Optional[list[CarePlan]]:
    #     """Validates that carePlan is not an empty list if provided."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("physical_examination")
    # @classmethod
    # def _physical_examination_not_empty(
    #     cls, v: Optional[list[Observation]], info: ValidationInfo
    # ) -> Optional[list[Observation]]:
    #     """Validates that physicalExamination is not an empty list if provided."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("allergies")
    # @classmethod
    # def _allergies_not_empty(
    #     cls, v: Optional[list[AllergyIntolerance]], info: ValidationInfo
    # ) -> Optional[list[AllergyIntolerance]]:
    #     """Validates that allergies is not an empty list if provided."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("medication_statements")
    # @classmethod
    # def _medication_statements_not_empty(
    #     cls, v: Optional[list[MedicationStatement]], info: ValidationInfo
    # ) -> Optional[list[MedicationStatement]]:
    #     """Validates that medicationStatements is not an empty list if provided."""
    #     return check_not_empty(v, info.field_name)
