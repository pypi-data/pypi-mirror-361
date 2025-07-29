import json
import logging
from typing import Any, Dict

from pydantic import BaseModel
from carestack.base.errors import ValidationError
from carestack.common.enums import (
    DOCUMENT_LINKING_ENDPOINTS,
    TRANSFORM_SOURCE_TO_INTERMEDIATE_PROMPT,
)
from carestack.document_linking.encounter_dto.source_dto.op_consultation_dto import (
    OpConsultationDTO as OpConsultationSourceDTO,
)
from carestack.document_linking.encounter_dto.intermediate_dto.op_consultation_dto import (
    AdvisoryNoteItem,
    AllergyItem,
    ConditionItem,
    CurrentMedicationItem,
    DocumentReferenceItem,
    FamilyHistoryItem,
    FollowUpItem,
    ImmunizationItem,
    InvestigationAdviceItem,
    OpConsultationDTO as OpConsultationIntermediateDTO,
    PhysicalExamination,
    PrescribedMedicationItem,
    ProcedureItem,
)
from carestack.document_linking.encounter_dto.target_dto.op_consult_record_dto import (
    OpConsultRecordDTO as OpConsultationTargetDTO,
)
from carestack.document_linking.transformer.transformer import Transformer
from carestack.document_linking.encounter_dto.intermediate_dto.sections_dto import (
    VitalSign,
)

logger = logging.getLogger(__name__)


class GetJsonFromTextResponse(BaseModel):
    response: str


class OpConsultationTransformer(
    Transformer[
        OpConsultationSourceDTO, OpConsultationIntermediateDTO, OpConsultationTargetDTO
    ]
):
    """
    Transformer for OpConsultation data.
    """

    async def source_to_intermediate(
        self, source_data: OpConsultationSourceDTO
    ) -> OpConsultationIntermediateDTO:
        """Transforms source data for OpConsultation to IntermediateDTO."""
        try:
            request_body: Dict[str, Any] = {
                "data": json.dumps(
                    source_data.model_dump(by_alias=True, exclude_none=True)
                ),
                "inputTextCot": TRANSFORM_SOURCE_TO_INTERMEDIATE_PROMPT,
                "responseSchema": {
                    "type": "schema",
                    "properties": {
                        "chiefComplaints": "string",
                        "physicalExamination": {
                            "bloodPressure": {"value": "string", "unit": "string"},
                            "heartRate": {"value": "string", "unit": "string"},
                            "respiratoryRate": {
                                "value": "string",
                                "unit": "string",
                            },
                            "temperature": {"value": "string", "unit": "string"},
                            "oxygenSaturation": {
                                "value": "string",
                                "unit": "string",
                            },
                            "height": {"value": "string", "unit": "string"},
                            "weight": {"value": "string", "unit": "string"},
                        },
                        "conditions": [{"description": "string", "status": "string"}],
                        "medicalHistory": [
                            {
                                "description": "string",
                                "status": "string",
                            },
                            {
                                "procedureText": "string",
                                "status": "string",
                                "complicationText": "string",
                                "performedDate": "string",
                            },
                        ],
                        "familyHistory": [
                            {
                                "relation": "string",
                                "healthNote": "string",
                                "status": "string",
                            }
                        ],
                        "allergies": [
                            {
                                "status": "string",
                                "verificationStatus": "string",
                                "recordedDate": "string",
                                "reaction": "string",
                            }
                        ],
                        "immunizations": [
                            {
                                "status": "string",
                                "brandName": "string",
                                "vaccineName": "string",
                                "vaccinatedDate": "string",
                                "lotNumber": "string",
                                "expirationDate": "string",
                            }
                        ],
                        "currentMedications": [
                            {
                                "status": "active",
                                "date Asserted": "2025",
                                "medication": "string",
                                "reason": "string",
                            }
                        ],
                        "investigationAdvice": [
                            {
                                "description": "string",
                                "status": "string",
                                "intent": "string",
                            }
                        ],
                        "prescribedMedications": [
                            {
                                "status": "string",
                                "authoredOn": "string",
                                "dosageDuration": "number",
                                "dosageFrequency": "string",
                                "medicationRoute": "string",
                                "medicationMethod": "string",
                                "medication": "string",
                                "reason": "string",
                            }
                        ],
                        "procedures": [
                            {
                                "status": "string",
                                "procedureText": "string",
                                "complicationText": "string",
                                "performedDate": "string",
                            }
                        ],
                        "advisoryNotes": [{"category": "string", "note": "string"}],
                        "followUps": [
                            {
                                "serviceCategory": "string",
                                "serviceType": "Consultation",
                                "appointmentType": "string",
                                "appointmentReference": "string",
                            }
                        ],
                        "opConsultDocuments": [{"base64File": "string"}],
                    },
                    "required": [
                        "chiefComplaints",
                        "physicalExamination",
                        "conditions",
                        "medicalHistory",
                        "familyHistory",
                        "allergies",
                        "immunizations",
                        "currentMedications",
                        "investigationAdvice",
                        "prescribedMedications",
                        "procedures",
                        "advisoryNotes",
                        "followUps",
                        "opConsultDocuments",
                    ],
                },
            }
            op_consultation_json = await self.post(
                DOCUMENT_LINKING_ENDPOINTS.GET_JSON_FROM_TEXT,
                data=request_body,
                response_model=GetJsonFromTextResponse,
            )
            logger.info(f"Received from self.post: {op_consultation_json!r}")
            physical_examination_data = PhysicalExamination(
                bloodPressure=VitalSign(value="120/80", unit="mmHg"),
                heartRate=VitalSign(value="72", unit="bpm"),
                respiratoryRate=VitalSign(value="16", unit="breaths/min"),
                temperature=VitalSign(value="98.6", unit="°F"),
                oxygenSaturation=VitalSign(value="98", unit="%"),
                height=VitalSign(value="175", unit="cm"),
                weight=VitalSign(value="70", unit="kg"),
            )

            condition_item_data = [
                ConditionItem(description="Hypertension", status="active"),
                ConditionItem(description="Diabetes", status="inactive"),
            ]

            medical_history_item_data = [
                ConditionItem(
                    description="Appendectomy",
                    status="resolved",
                ),
                ProcedureItem(
                    procedureText="Tonsillectomy",
                    status="resolved",
                    complicationText="Postoperative bleeding",
                    performedDate="2005-02-20",
                ),
            ]

            family_history_item_data = [
                FamilyHistoryItem(
                    relation="Father", healthNote="Heart disease", status="present"
                )
            ]

            allergy_item_data = [
                AllergyItem(
                    status="active",
                    verificationStatus="confirmed",
                    recordedDate="2015-03-10",
                    reaction="Rash",
                ),
                AllergyItem(
                    status="active",
                    verificationStatus="confirmed",
                    recordedDate="2018-07-22",
                    reaction="Swelling",
                ),
            ]

            immunization_item_data = [
                ImmunizationItem(
                    status="completed",
                    brandName="Pfizer",
                    vaccineName="COVID-19",
                    vaccinatedDate="2021-04-15",
                    lotNumber="ABC12345",
                    expirationDate="2023-04-15",
                ),
                ImmunizationItem(
                    status="completed",
                    brandName="Moderna",
                    vaccineName="COVID-19",
                    vaccinatedDate="2021-05-15",
                    lotNumber="XYZ67890",
                    expirationDate="2023-05-15",
                ),
            ]

            current_medication_item_data = [
                CurrentMedicationItem(
                    status="active",
                    dateAsserted="2022-01-05",
                    medication="Metformin",
                    reason="Diabetes",
                ),
                CurrentMedicationItem(
                    status="active",
                    dateAsserted="2022-03-12",
                    medication="Lisinopril",
                    reason="Hypertension",
                ),
            ]

            investigation_advice_item_data = [
                InvestigationAdviceItem(
                    description="Blood glucose test", status="pending", intent="order"
                ),
                InvestigationAdviceItem(
                    description="Lipid panel", status="pending", intent="order"
                ),
            ]

            prescribed_medication_item_data = [
                PrescribedMedicationItem(
                    status="active",
                    authoredOn="2023-01-10",
                    dosageDuration=30,
                    dosageFrequency="daily",
                    medicationRoute="oral",
                    medicationMethod="tablet",
                    medication="Metformin",
                    reason="Diabetes",
                ),
                PrescribedMedicationItem(
                    status="active",
                    authoredOn="2023-03-15",
                    dosageDuration=30,
                    dosageFrequency="daily",
                    medicationRoute="oral",
                    medicationMethod="tablet",
                    medication="Lisinopril",
                    reason="Hypertension",
                ),
            ]

            procedure_item_data = [
                ProcedureItem(
                    status="completed",
                    procedureText="Colonoscopy",
                    complicationText="Postoperative bleeding",
                    performedDate="2022-06-20",
                ),
            ]

            advisory_note_item_data = [
                AdvisoryNoteItem(
                    category="Diet", note="Eat more fruits and vegetables."
                ),
                AdvisoryNoteItem(
                    category="Exercise", note="Exercise for 30 minutes daily."
                ),
            ]

            follow_up_item_data = [
                FollowUpItem(
                    serviceCategory="Cardiology",
                    serviceType="Consultation",
                    appointmentType="In-person",
                    appointmentReference="1234567890",
                ),
                FollowUpItem(
                    serviceCategory="Endocrinology",
                    serviceType="Consultation",
                    appointmentType="In-person",
                    appointmentReference="9876543210",
                ),
            ]

            op_consult_document_item_data = [
                DocumentReferenceItem(base64File="base64_encoded_file_content_1"),
                DocumentReferenceItem(base64File="base64_encoded_file_content_2"),
            ]

            # Example OpConsultationDTO object
            op_consultation_dto_example = OpConsultationIntermediateDTO(
                chiefComplaints="Headache and fatigue",
                physicalExamination=physical_examination_data,
                conditions=condition_item_data,
                medicalHistory=medical_history_item_data,
                familyHistory=family_history_item_data,
                allergies=allergy_item_data,
                immunizations=immunization_item_data,
                currentMedications=current_medication_item_data,
                investigationAdvice=investigation_advice_item_data,
                prescribedMedications=prescribed_medication_item_data,
                procedures=procedure_item_data,
                advisoryNotes=advisory_note_item_data,
                followUps=follow_up_item_data,
                opConsultDocuments=op_consult_document_item_data,
            )

            # if response_string is None:
            #     raise ValueError(
            #         "Invalid API response: 'response' key is missing or None"
            #     )
            op_consultation_json = self.convert_string_to_json(
                op_consultation_json.response
            )
            response = OpConsultationIntermediateDTO(**op_consultation_json)
            # if op_consultation_json is None or not hasattr(
            #     op_consultation_json, "response"
            # ):
            #     logger.error(
            #         "API call returned None or object without 'response' attribute."
            #     )
            #     raise ValueError(
            #         "Failed to get valid response object from GET_JSON_FROM_TEXT"
            #     )

            # json_string = op_consultation_json.response
            # logger.info(f"Extracted json_string: {json_string!r}")
            # if json_string is None:
            #     raise ValueError(
            #         "Invalid API response: 'response' key is missing or None"
            #     )

            # Parse the JSON string
            # print("JSON response string = ", json_string)  # Optional: for debugging
            # parsed_json_data = self.convert_string_to_json(json_string)
            # print(
            #     "Parsed JSON response = ", parsed_json_data
            # )  # Optional: for debugging

            # Instantiate the Intermediate DTO from the parsed data
            # intermediate_dto = OpConsultationIntermediateDTO(**parsed_json_data)

            # Re
            return response

        except (KeyError, TypeError) as e:
            raise ValueError(f"Invalid source data format for OpConsultation: {e}")
        except ValidationError as e:
            raise ValueError(f"Invalid data for OpConsultation: {e}") from e

    async def intermediate_to_target(
        self, intermediate_dto: OpConsultationIntermediateDTO
    ) -> OpConsultationTargetDTO:
        """Transforms IntermediateDTO for OpConsultation to target DTO."""
        try:

            target_dto = OpConsultationTargetDTO(
                chiefComplaints=intermediate_dto.chief_complaints,
                physicalExamination=self.get_physical_examination(
                    intermediate_dto.physical_examination
                ),
                medicalHistory=self.get_medical_history(
                    intermediate_dto.medical_history
                ),
                familyHistory=self.get_family_history(intermediate_dto.family_history),
                allergies=self.get_allergies(intermediate_dto.allergies),
                conditions=self.get_conditions(intermediate_dto.conditions),
                medications=self.get_medications(
                    intermediate_dto.current_medications,
                    intermediate_dto.prescribed_medications,
                ),
                investigationAdvice=self.get_investigation_advices(
                    intermediate_dto.investigation_advice
                ),
                procedures=self.get_procedures(intermediate_dto.procedures),
                advisoryNotes=self.get_advisory_notes(intermediate_dto.advisory_notes),
                followUps=self.get_follow_ups(intermediate_dto.follow_ups),
                opConsultDocuments=self.get_document_references(
                    intermediate_dto.op_consult_documents
                ),
            )
            return target_dto
        except (KeyError, TypeError) as e:
            raise ValueError(
                f"Invalid intermediate data format for OpConsultation: {e}"
            )
        except ValidationError as e:
            raise ValueError(f"Invalid data for OpConsultation: {e}") from e
