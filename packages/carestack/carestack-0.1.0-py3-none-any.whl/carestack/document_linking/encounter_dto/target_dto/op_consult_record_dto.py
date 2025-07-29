from typing import Optional, Union
from pydantic import BaseModel, Field, field_validator

from carestack.document_linking.encounter_dto.target_dto.advisory_note_dto import (
    AdvisoryNote,
)
from carestack.document_linking.encounter_dto.target_dto.allergy_intolerance_dto import (
    AllergyIntolerance,
)
from carestack.document_linking.encounter_dto.target_dto.care_plan_dto import (
    CarePlan,
)
from carestack.document_linking.encounter_dto.target_dto.document_reference_dto import (
    DocumentReference,
)
from carestack.document_linking.encounter_dto.target_dto.follow_up_dto import (
    FollowUp,
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
from carestack.document_linking.encounter_dto.target_dto.service_request_dto import (
    ServiceRequest,
)

from carestack.document_linking.encounter_dto.target_dto.condition_dto import (
    Condition,
)


def transform_to_condition_or_procedure(obj: dict) -> Union[Condition, Procedure]:
    """Transforms a dictionary to a Condition or Procedure object."""
    if "procedure" in obj:
        return Procedure(**obj)
    return Condition(**obj)


def transform_to_medication_request_or_statement(
    obj: dict,
) -> Union[MedicationRequest, MedicationStatement]:
    """Transforms a dictionary to a MedicationRequest or MedicationStatement object."""
    if "dosageInstruction" in obj:
        return MedicationRequest(**obj)
    return MedicationStatement(**obj)


class OpConsultRecordDTO(BaseModel):
    """Represents an outpatient consultation record."""

    chief_complaints: str = Field(..., alias="chiefComplaints")
    physical_examination: list[Observation] = Field(alias="physicalExamination")
    medical_history: Optional[list[Union[Condition, Procedure]]] = Field(
        None, alias="medicalHistory"
    )
    family_history: Optional[MedicationHistory] = Field(None, alias="familyHistory")
    allergies: Optional[list[AllergyIntolerance]] = Field(None, alias="allergies")
    conditions: list[Condition] = Field(alias="conditions")
    medications: Optional[list[Union[MedicationStatement, MedicationRequest]]] = Field(
        None, alias="medications"
    )
    investigation_advice: Optional[list[ServiceRequest]] = Field(
        None, alias="investigationAdvice"
    )
    advisory_notes: Optional[list[AdvisoryNote]] = Field(None, alias="advisoryNotes")
    procedures: Optional[list[Procedure]] = Field(None, alias="procedures")
    follow_ups: Optional[list[FollowUp]] = Field(None, alias="followUps")
    op_consult_documents: Optional[list[DocumentReference]] = Field(
        None, alias="opConsultDocuments"
    )

    # @field_validator("medications", mode="before")
    # @classmethod
    # def _medications_transform(
    #     cls, v: Optional[list[dict]]
    # ) -> Optional[list[Union[MedicationStatement, MedicationRequest]]]:
    #     """Transforms and validates the medications list."""
    #     if v is None:
    #         return None
    #     transformed_medications: list[Union[MedicationStatement, MedicationRequest]] = (
    #         []
    #     )
    #     for medication_item in v:
    #         transformed_medications.append(
    #             transform_to_medication_request_or_statement(medication_item)
    #         )
    #     return transformed_medications

    # @field_validator("medical_history")
    # @classmethod
    # def _medical_history_transform(
    #     cls, v: Optional[list[dict]]
    # ) -> Optional[list[Union[Condition, Procedure]]]:
    #     """Transforms and validates the medical history list."""
    #     if v is None:
    #         return None
    #     return [transform_to_condition_or_procedure(item) for item in v]
