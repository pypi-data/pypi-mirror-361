from abc import ABC, abstractmethod
import asyncio
import json
import re
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

import httpx

from carestack.base.base_service import BaseService
from carestack.common.enums import (
    DOCUMENT_LINKING_ENDPOINTS,
    VITALS_REFERENCE_RANGES,
    CarePlanIntent,
    CarePlanStatus,
    ClinicalStatus,
    DosageFrequency,
    MedicationMethod,
    MedicationRequestStatus,
    MedicationRoute,
    MedicationStatementStatus,
    ObservationStatus,
    ProcedureStatus,
    ServiceRequestIntent,
    ServiceRequestStatus,
    VerificationStatus,
)

from carestack.document_linking.encounter_dto.target_dto.advisory_note_dto import (
    AdvisoryNote,
)
from carestack.document_linking.encounter_dto.target_dto.allergy_intolerance_dto import (
    AllergyIntolerance,
)
from carestack.document_linking.encounter_dto.target_dto.condition_dto import Condition
from carestack.document_linking.encounter_dto.target_dto.document_reference_dto import (
    DocumentReference,
)
from carestack.document_linking.encounter_dto.target_dto.dosage_instruction_dto import (
    DosageInstruction,
)
from carestack.document_linking.encounter_dto.target_dto.follow_up_dto import FollowUp
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
from carestack.document_linking.encounter_dto.target_dto.op_consult_record_dto import (
    OpConsultRecordDTO,
)
from carestack.document_linking.encounter_dto.target_dto.procedure_dto import Procedure
from carestack.document_linking.encounter_dto.target_dto.reference_range_dto import (
    ReferenceRange,
)
from carestack.document_linking.encounter_dto.target_dto.service_request_dto import (
    ServiceRequest,
)
from carestack.document_linking.encounter_dto.target_dto.snomed_code_dto import (
    ClosestTerm,
    SearchResultListResponse,
    SearchResultResponse,
    SnomedCode,
)
from carestack.document_linking.encounter_dto.target_dto.value_quantity_dto import (
    ValueQuantity,
)
from carestack.document_linking.encounter_dto.intermediate_dto.sections_dto import (
    AdvisoryNoteItem,
    AllergyItem,
    CarePlanItem,
    ConditionItem,
    CurrentMedicationItem,
    DocumentReferenceItem,
    FamilyHistoryItem,
    FollowUpItem,
    InvestigationAdviceItem,
    PhysicalExamination,
    PrescribedMedicationItem,
    ProcedureItem,
    VitalSign,
)
from carestack.document_linking.encounter_dto.target_dto.care_plan_dto import (
    CarePlan,
)

# Define a type variable for the source data type
SourceDTO = TypeVar("SourceDTO")
# Define a type variable for the intermediate data type
IntermediateDTO = TypeVar("IntermediateDTO")
# Define a type variable for the target data type
TargetDTO = TypeVar("TargetDTO")


class Transformer(Generic[SourceDTO, IntermediateDTO, TargetDTO], BaseService, ABC):
    """
    Generic interface for transforming data between source, intermediate, and target formats.
    """

    @abstractmethod
    def source_to_intermediate(self, source_data: SourceDTO) -> IntermediateDTO:
        """
        Transforms source data to IntermediateDTO.

        Args:
            source_data: The source data to transform.

        Returns:
            The transformed IntermediateDTO.
        """
        pass

    @abstractmethod
    def intermediate_to_target(self, intermediate_dto: IntermediateDTO) -> TargetDTO:
        """
        Transforms IntermediateDTO to target data.

        Args:
            intermediate_dto: The IntermediateDTO to transform.

        Returns:
            The transformed target data.
        """
        pass

    def convert_string_to_json(self, json_string: str) -> dict[str, Any]:
        """
        Converts a string representation of a JSON object to a Python dictionary.

        Args:
            json_string: The string to convert.

        Returns:
            A dictionary representing the JSON object.

        Raises:
            json.JSONDecodeError: If the string is not valid JSON.
        """
        try:
            # Remove trailing comma if present
            cleaned_str = re.sub(r"```json|```", "", json_string).strip()
            if cleaned_str.strip().endswith(","):
                cleaned_str = cleaned_str.strip()[:-1]

            # Remove extra new lines
            cleaned_str = cleaned_str.replace("\n", "")

            # Add missing closing bracket
            if not cleaned_str.strip().endswith("}"):
                cleaned_str = cleaned_str.strip() + "}"

            # Replace single quotes with double quotes
            cleaned_str = cleaned_str.replace("'", '"')

            # Replace None with null
            cleaned_str = cleaned_str.replace("None", "null")

            # Replace True with true
            cleaned_str = cleaned_str.replace("True", "true")

            # Replace False with false
            cleaned_str = cleaned_str.replace("False", "false")

            # Replace extra characters
            cleaned_str = cleaned_str.replace("\\u00b0", "")

            # Replace invalid data
            cleaned_str = cleaned_str.replace(" .", "")

            json_object = json.loads(cleaned_str)
            return json_object
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON string: {e.msg} - Original string: {json_string}",
                e.doc,
                e.pos,
            ) from e

    def __levenshtein_distance(self, actual_name: str, name_to_match: str) -> int:
        string1 = actual_name.strip().lower() if actual_name else ""
        string2 = name_to_match.strip().lower() if name_to_match else ""
        l1, l2 = len(string1), len(string2)

        if l1 == 0:
            return l2
        if l2 == 0:
            return l1

        d = [[0] * (l2 + 1) for _ in range(l1 + 1)]

        for i in range(l1 + 1):
            d[i][0] = i
        for j in range(l2 + 1):
            d[0][j] = j

        for i in range(1, l1 + 1):
            for j in range(1, l2 + 1):
                if string1[i - 1] == string2[j - 1]:
                    d[i][j] = d[i - 1][j - 1]
                else:
                    d[i][j] = min(
                        d[i - 1][j] + 1,  # deletion
                        d[i][j - 1] + 1,  # insertion
                        d[i - 1][j - 1] + 1,  # substitution
                    )

        return d[l1][l2]

    def __get_closest_term(
        self, snomed_data: list[SearchResultResponse], search_term: str
    ) -> Optional[ClosestTerm]:
        """
        Finds the closest term in a list of SNOMED data to a given search term using Levenshtein distance.

        Args:
            snomed_data: A list of SearchResultResponse objects, each containing a term and a code.
            search_term: The term to search for the closest match to.

        Returns:
            A dictionary containing the closest term, its code, and the minimum Levenshtein distance,
            or None if the snomed_data list is empty.
        """
        if not snomed_data:
            return None

        closest_term = None
        min_distance = float("inf")

        for item in snomed_data:
            distance = self.__levenshtein_distance(
                item.term.lower(), search_term.lower()
            )
            if distance < min_distance:
                min_distance = distance
                closest_term = item

        if closest_term:
            return ClosestTerm(
                term=closest_term.term,
                code=closest_term.code,
                min_distance=int(min_distance),
            )

        return None

    async def _get_snomed_code(
        self, semantic_tag: str, search_term: str
    ) -> Optional[SnomedCode]:
        try:

            requestBody = {"semantics": semantic_tag, "searchTerm": search_term}
            response = await self.post(
                DOCUMENT_LINKING_ENDPOINTS.GET_SNOMED_CODES,
                data=requestBody,
                response_model=SearchResultListResponse,
            )
            search_results: list[SearchResultResponse] = response.root
            closest_term = self.__get_closest_term(search_results, search_term)
            if closest_term:
                return SnomedCode(code=closest_term.code, text=closest_term.term)
            else:
                # If no exact match, try splitting the search term and searching again
                if " " in search_term:
                    parts = search_term.split()
                    for part in parts:
                        if len(part) > 2:
                            requestBody = {
                                "semantics": semantic_tag,
                                "searchTerm": part,
                            }
                            response = await self.post(
                                DOCUMENT_LINKING_ENDPOINTS.GET_SNOMED_CODES,
                                data=requestBody,
                                response_model=SearchResultListResponse,
                            )
                            search_results: list[SearchResultResponse] = response.root
                            closest_term = self.__get_closest_term(search_results, part)
                            if closest_term:
                                return SnomedCode(
                                    code=closest_term.code, text=closest_term.term
                                )
                return None
        except httpx.HTTPError as e:
            print(f"HTTP error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        return None

    async def update_snomed_codes(self, targetDTO: TargetDTO) -> TargetDTO:
        """
        update the SNOMED codes in the target DTO.

        Args:
            targetDTO: The target DTO to update snomed codes.
        """
        search_term_semantic_map = {}

        # if encounter is opConsultation Encounter then we should map all those search terms to the semantic tags and create the map.
        if isinstance(targetDTO, OpConsultRecordDTO):

            # update snomed codes for physical examination,for physical examination we can set the snomed codes directly.
            codes = [
                "75367002",  # blood pressure
                "364075005",  # heart rate
                "86290005",  # respiratory rate
                "703421000",  # temperature
                "103228002",  # oxygen saturation
                "1153637007",  # height
                "27113001",  # weight
            ]
            for i, code in enumerate(codes):
                pe = targetDTO.physical_examination[i]
                pe.code = code
                pe.value_quantity.code = code
                pe.reference_range.low.code = code
                pe.reference_range.high.code = code

            # update snomed codes for medical history
            if targetDTO.medical_history is not None:
                for section in targetDTO.medical_history:
                    if isinstance(section, Condition):
                        search_term_semantic_map.setdefault("condition", set()).add(
                            section.text
                        )
                    elif isinstance(section, Procedure):
                        search_term_semantic_map.setdefault(
                            "procedure_complication", set()
                        ).add(section.complications.text)
                        search_term_semantic_map.setdefault("procedure", set()).add(
                            section.text
                        )

            # update snomed codes for family history
            if targetDTO.family_history is not None:
                for condition in targetDTO.family_history.conditions:
                    search_term_semantic_map.setdefault("condition", set()).add(
                        condition.text
                    )
                for procedure in targetDTO.family_history.procedures:
                    search_term_semantic_map.setdefault("procedure", set()).add(
                        procedure.text
                    )
                    search_term_semantic_map.setdefault(
                        "procedure_complication", set()
                    ).add(procedure.complications.text)

            # update snomed codes for allergies
            if targetDTO.allergies is not None:
                for allergy in targetDTO.allergies:
                    search_term_semantic_map.setdefault("allergy_symptoms", set()).add(
                        allergy.reaction
                    )

            # update snomed codes for conditions
            if targetDTO.conditions is not None:
                for condition in targetDTO.conditions:
                    search_term_semantic_map.setdefault("condition", set()).add(
                        condition.text
                    )

            # update snomed codes for medications
            if targetDTO.medications is not None:
                for medication in targetDTO.medications:
                    if isinstance(medication, MedicationRequest) or isinstance(
                        medication, MedicationStatement
                    ):
                        search_term_semantic_map.setdefault("medication", set()).add(
                            medication.text
                        )
                        search_term_semantic_map.setdefault("condition", set()).add(
                            medication.reason_code.text
                        )

            # update snomed codes for investigation_advice
            if targetDTO.investigation_advice is not None:
                for investigation in targetDTO.investigation_advice:
                    if isinstance(investigation, ServiceRequest):
                        search_term_semantic_map.setdefault("procedure", set()).add(
                            investigation.text
                        )

            # update snomed codes for advisory_notes
            if targetDTO.advisory_notes is not None:
                for advisory in targetDTO.advisory_notes:
                    search_term_semantic_map.setdefault("observation", set()).add(
                        advisory.note.text
                    )
                    search_term_semantic_map.setdefault("observation", set()).add(
                        advisory.category.text
                    )

            # update snomed codes for procedures
            if targetDTO.procedures is not None:
                for procedure in targetDTO.procedures:
                    search_term_semantic_map.setdefault("procedure", set()).add(
                        procedure.text
                    )
                    search_term_semantic_map.setdefault(
                        "procedure_complication", set()
                    ).add(procedure.complications.text)
            # update snomed codes for follow_ups
            if targetDTO.follow_ups is not None:
                for follow_up in targetDTO.follow_ups:
                    search_term_semantic_map.setdefault("procedure", set()).add(
                        follow_up.service_type.text
                    )
                    search_term_semantic_map.setdefault("procedure", set()).add(
                        follow_up.service_category.text
                    )
                    search_term_semantic_map.setdefault("procedure", set()).add(
                        follow_up.appointment_type.text
                    )

            print("search_term_semantic_map = ", search_term_semantic_map)

            snomed_code_map: Dict[str, Dict[str, SnomedCode]] = {}
            async with httpx.AsyncClient() as client:
                tasks = []
                for semantic_tag, search_terms in search_term_semantic_map.items():
                    snomed_code_map[semantic_tag] = {}
                    for search_term in search_terms:
                        tasks.append(self._get_snomed_code(semantic_tag, search_term))
                results = await asyncio.gather(*tasks)
                print("results = ", results)
                i = 0
                for semantic_tag, search_terms in search_term_semantic_map.items():
                    for search_term in search_terms:
                        if results[i]:
                            snomed_code_map[semantic_tag][search_term] = results[i]
                        i += 1

            print("snomed_code_map = ", snomed_code_map)

            if isinstance(targetDTO, OpConsultRecordDTO):
                for section_name, term_code_map in snomed_code_map.items():
                    if section_name == "condition":
                        if targetDTO.medical_history is not None:
                            for section in targetDTO.medical_history:
                                if isinstance(section, Condition):
                                    if section.text in term_code_map:
                                        section.code = term_code_map[section.text].code
                        for condition in targetDTO.conditions:
                            if condition.text in term_code_map:
                                condition.code = term_code_map[condition.text].code
                        if targetDTO.family_history is not None:
                            for condition in targetDTO.family_history.conditions:
                                if condition.text in term_code_map:
                                    condition.code = term_code_map[condition.text].code

                    elif section_name == "procedure":
                        if targetDTO.medical_history is not None:
                            for section in targetDTO.medical_history:
                                if isinstance(section, Procedure):
                                    if section.text in term_code_map:
                                        section.code = term_code_map[section.text].code
                        if targetDTO.procedures is not None:
                            for procedure in targetDTO.procedures:
                                if procedure.text in term_code_map:
                                    procedure.code = term_code_map[procedure.text].code
                                    procedure.procedure.code = term_code_map[
                                        procedure.text
                                    ].code
                        if targetDTO.family_history is not None:
                            for procedure in targetDTO.family_history.procedures:
                                if procedure.text in term_code_map:
                                    procedure.code = term_code_map[procedure.text].code
                        if targetDTO.follow_ups is not None:
                            for follow_up in targetDTO.follow_ups:
                                if follow_up.service_type.text in term_code_map:
                                    follow_up.service_type.code = term_code_map[
                                        follow_up.service_type.text
                                    ].code
                                if follow_up.service_category.text in term_code_map:
                                    follow_up.service_category.code = term_code_map[
                                        follow_up.service_category.text
                                    ].code
                                if follow_up.appointment_type.text in term_code_map:
                                    follow_up.appointment_type.code = term_code_map[
                                        follow_up.appointment_type.text
                                    ].code
                        if targetDTO.investigation_advice is not None:
                            for investigation in targetDTO.investigation_advice:
                                if investigation.text in term_code_map:
                                    investigation.code = term_code_map[
                                        investigation.text
                                    ].code

                    elif section_name == "procedure_complication":
                        if targetDTO.medical_history is not None:
                            for section in targetDTO.medical_history:
                                if isinstance(section, Procedure):
                                    if section.complications.text in term_code_map:
                                        section.complications.code = term_code_map[
                                            section.complications.text
                                        ].code
                        if targetDTO.procedures is not None:
                            for procedure in targetDTO.procedures:
                                if procedure.complications.text in term_code_map:
                                    procedure.complications.code = term_code_map[
                                        procedure.complications.text
                                    ].code
                        if targetDTO.family_history is not None:
                            for procedure in targetDTO.family_history.procedures:
                                if procedure.complications.text in term_code_map:
                                    procedure.complications.code = term_code_map[
                                        procedure.complications.text
                                    ].code

                    elif section_name == "allergy_symptoms":
                        if targetDTO.allergies is not None:
                            for allergy in targetDTO.allergies:
                                if allergy.reaction in term_code_map:
                                    allergy.code = term_code_map[allergy.reaction].code

                    elif section_name == "medication":
                        if targetDTO.medications is not None:
                            for medication in targetDTO.medications:
                                if medication.text in term_code_map:
                                    medication.code = term_code_map[
                                        medication.text
                                    ].code
                                    medication.medication.code = term_code_map[
                                        medication.text
                                    ].code
                                    medication.reason_code.code = term_code_map[
                                        medication.text
                                    ].code

                    elif section_name == "observation":
                        if targetDTO.advisory_notes is not None:
                            for advisory in targetDTO.advisory_notes:
                                if advisory.note.text in term_code_map:
                                    advisory.note.code = term_code_map[
                                        advisory.note.text
                                    ].code
                                if advisory.category.text in term_code_map:
                                    advisory.category.code = term_code_map[
                                        advisory.category.text
                                    ].code
        print("targetDTO with updated snomed ", targetDTO)
        return targetDTO

    def __get_observation(self, vitals: VitalSign, type: str) -> Observation:
        return Observation(
            code="",
            text=type,
            status=ObservationStatus.REGISTERED,
            effectiveDateTime="04-07-2025",
            valueQuantity=ValueQuantity(
                value=vitals.value,
                unit=vitals.unit,
                code="",
            ),
            referenceRange=ReferenceRange(
                low=ValueQuantity(
                    value=str(
                        VITALS_REFERENCE_RANGES.get(type, {})
                        .get(vitals.value, {})
                        .get("low", 0)
                    ),
                    unit=vitals.unit,
                    code="",
                ),
                high=ValueQuantity(
                    value=str(
                        VITALS_REFERENCE_RANGES.get(type, {})
                        .get(vitals.value, {})
                        .get("high", 0)
                    ),
                    unit=vitals.unit,
                    code="",
                ),
            ),
        )

    def __get_condition(self, condition: ConditionItem) -> Condition:
        return Condition(
            code="", text=condition.description, clinicalStatus=ClinicalStatus.ACTIVE
        )

    def __get_procedure(self, procedure: ProcedureItem) -> Procedure:
        return Procedure(
            code="",
            text=procedure.procedure_text,
            status=ProcedureStatus.COMPLETED,
            procedure=SnomedCode(code="", text=procedure.procedure_text),
            complications=SnomedCode(
                code="",
                text=procedure.complication_text,
            ),
            performedDate=procedure.performed_date,
        )

    def __get_allergy(self, allergy: AllergyItem) -> AllergyIntolerance:
        return AllergyIntolerance(
            code="",
            text=allergy.reaction,
            clinicalStatus=ClinicalStatus.ACTIVE,
            verificationStatus=VerificationStatus.CONFIRMED,
            recordedDate=allergy.recorded_date,
            reaction=allergy.reaction,
        )

    def __get_medication_statement(
        self, medication: CurrentMedicationItem
    ) -> MedicationStatement:
        return MedicationStatement(
            code="",
            text=medication.medication,
            status=MedicationStatementStatus.ACTIVE,
            dateAsserted=medication.date_asserted,
            reasonCode=SnomedCode(code="", text=medication.reason),
            medication=SnomedCode(code="", text=medication.medication),
        )

    def __get_medication_request(
        self, medication: PrescribedMedicationItem
    ) -> MedicationRequest:
        return MedicationRequest(
            code="",
            text=medication.medication,
            status=MedicationRequestStatus.ACTIVE,
            authoredOn=medication.authored_on,
            dosageInstruction=DosageInstruction(
                duration=medication.dosage_duration,
                frequency=DosageFrequency.TWICE,
                route=MedicationRoute.ORAL,
                method=MedicationMethod.SWALLOW,
            ),
            medication=SnomedCode(code="", text=medication.medication),
            reasonCode=SnomedCode(code="", text=medication.reason),
        )

    def __get_service_request(
        self, service_request: InvestigationAdviceItem
    ) -> ServiceRequest:
        return ServiceRequest(
            code="",
            text=service_request.description,
            status=ServiceRequestIntent.ACTIVE,
            intent=ServiceRequestStatus.ORDER,
        )

    def __get_advisory_note(self, advisory_note: AdvisoryNoteItem) -> AdvisoryNote:
        return AdvisoryNote(
            category=SnomedCode(code="", text=advisory_note.category),
            note=SnomedCode(code="", text=advisory_note.note),
        )

    def __get_follow_up(self, follow_up: FollowUpItem) -> FollowUp:
        return FollowUp(
            serviceCategory=SnomedCode(code="", text=follow_up.service_category),
            serviceType=SnomedCode(code="", text=follow_up.service_type),
            appointmentType=SnomedCode(code="", text=follow_up.appointment_type),
            appointmentReference=follow_up.appointment_reference,
        )

    def _care_plan(self, care_plan: CarePlanItem) -> CarePlan:
        return CarePlan(
            category=SnomedCode(code="", text=care_plan.description),
            status=CarePlanStatus.ACTIVE,
            intent=CarePlanIntent.PLAN,
            title=care_plan.title,
        )

    def get_physical_examination(
        self, physical_examination: PhysicalExamination
    ) -> list[Observation]:
        """
        Converts a PhysicalExamination object to a list of Observation objects.

        Args:
            physical_examination: The PhysicalExamination object to convert.

        Returns:
            A list of Observation objects.
        """
        if physical_examination is None:
            return []

        observations = []

        if physical_examination.blood_pressure:
            observations.append(
                self.__get_observation(
                    physical_examination.blood_pressure, "blood_pressure"
                )
            )
        if physical_examination.heart_rate:
            observations.append(
                self.__get_observation(physical_examination.heart_rate, "heart_rate")
            )
        if physical_examination.respiratory_rate:
            observations.append(
                self.__get_observation(
                    physical_examination.respiratory_rate, "respiratory_rate"
                )
            )
        if physical_examination.temperature:
            observations.append(
                self.__get_observation(physical_examination.temperature, "temperature")
            )
        if physical_examination.oxygen_saturation:
            observations.append(
                self.__get_observation(
                    physical_examination.oxygen_saturation, "oxygen_saturation"
                )
            )
        if physical_examination.height:
            observations.append(
                self.__get_observation(physical_examination.height, "height")
            )
        if physical_examination.weight:
            observations.append(
                self.__get_observation(physical_examination.weight, "weight")
            )

        return observations

    def get_conditions(self, conditions: list[ConditionItem]) -> list[Condition]:
        """
        Converts a list of ConditionItem objects to a list of Condition objects.

        Args:
            conditions: The list of ConditionItem objects to convert.

        Returns:
            A list of Condition objects.
        """
        conditions_list = []
        if conditions is None:
            return conditions_list
        for condition in conditions:
            conditions_list.append(self.__get_condition(condition))
        return conditions_list

    def get_medical_history(
        self, medical_history: list[ConditionItem | ProcedureItem]
    ) -> list[Union[Condition, Procedure]]:
        """
        Converts a list of ConditionItem objects to a list of Condition objects.

        Args:
            medical_history: The list of ConditionItem objects to convert.

        Returns:
            A list of Condition objects.
        """
        medical_history_list = []
        if medical_history is None:
            return medical_history_list
        for section in medical_history:
            if isinstance(section, ConditionItem):
                medical_history_list.append(self.__get_condition(section))
            elif isinstance(section, ProcedureItem):
                medical_history_list.append(self.__get_procedure(section))

        return medical_history_list

    def get_family_history(
        self, family_history: list[FamilyHistoryItem]
    ) -> MedicationHistory:
        condition_items = [
            ConditionItem(status=item.status, description=item.health_note)
            for item in family_history
        ]
        return MedicationHistory(
            conditions=self.get_conditions(condition_items), procedures=[]
        )

    def get_allergies(self, allergies: list[AllergyItem]) -> list[AllergyIntolerance]:
        allergies_list = []
        if allergies is None:
            return allergies_list
        for allergy in allergies:
            allergies_list.append(self.__get_allergy(allergy))
        return allergies_list

    def get_medications(
        self,
        current_medications: list[CurrentMedicationItem],
        prescribed_medications: list[PrescribedMedicationItem],
    ) -> list[MedicationRequest | MedicationStatement]:
        medications_list = []
        # for each_medication in current_medications:
        #     medications_list.append(self.__get_medication_statement(each_medication))
        for each_medication in prescribed_medications:
            medications_list.append(self.__get_medication_request(each_medication))
        return medications_list

    def get_procedures(self, procedures: list[ProcedureItem]) -> list[Procedure]:
        procedures_list = []
        if procedures is None:
            return procedures_list
        for procedure in procedures:
            procedures_list.append(self.__get_procedure(procedure))
        return procedures_list

    def get_investigation_advices(
        self, investigation_advice: list[InvestigationAdviceItem]
    ) -> list[ServiceRequest]:
        investigation_advice_list = []
        if investigation_advice is None:
            return investigation_advice_list
        for advice in investigation_advice:
            investigation_advice_list.append(self.__get_service_request(advice))
        return investigation_advice_list

    def get_advisory_notes(
        self, advisory_notes: list[AdvisoryNoteItem]
    ) -> list[AdvisoryNote]:
        advisory_notes_list = []
        if advisory_notes is None:
            return advisory_notes_list
        for note in advisory_notes:
            advisory_notes_list.append(self.__get_advisory_note(note))
        return advisory_notes_list

    def get_follow_ups(self, follow_ups: list[FollowUpItem]) -> list[FollowUp]:
        follow_ups_list = []
        if follow_ups is None:
            return follow_ups_list
        for follow_up in follow_ups:
            follow_ups_list.append(self.__get_follow_up(follow_up))
        return follow_ups_list

    def get_document_references(
        self, document_references: list[DocumentReferenceItem]
    ) -> list[DocumentReference]:
        document_references_list = []
        if document_references is None:
            return document_references_list
        for document_reference in document_references:
            document_references_list.append(
                DocumentReference(
                    contentType="application/pdf",
                    data=document_reference.base64_file,
                )
            )
        return document_references_list
