from enum import Enum


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class PatientIdTypeEnum(Enum):
    ABHA = "ABHA"
    AADHAAR = "AADHAAR"
    PAN = "PAN"
    DRIVING_LICENSE = "DRIVING_LICENSE"


class PatientTypeEnum(Enum):
    OLD = "OLD"
    NEW = "NEW"


class StatesAndUnionTerritories(Enum):
    ANDHRA_PRADESH = "Andhra Pradesh"
    ARUNACHAL_PRADESH = "Arunachal Pradesh"
    ASSAM = "Assam"
    BIHAR = "Bihar"
    CHATTISGARH = "Chattisgarh"
    GOA = "Goa"
    GUJARAT = "Gujarat"
    HARYANA = "Haryana"
    HIMACHAL_PRADESH = "Himachal Pradesh"
    JHARKHAND = "Jharkhand"
    KARNATAKA = "Karnataka"
    KERALA = "Kerala"
    MADHYA_PRADESH = "Madhya Pradesh"
    MAHARASHTRA = "Maharashtra"
    MANIPUR = "Manipur"
    MEGHALAYA = "Meghalaya"
    MIZORAM = "Mizoram"
    NAGALAND = "Nagaland"
    ODISHA = "Odisha"
    PUNJAB = "Punjab"
    RAJASTHAN = "Rajasthan"
    SIKKIM = "Sikkim"
    TAMIL_NADU = "Tamil Nadu"
    TELANGANA = "Telangana"
    TRIPURA = "Tripura"
    UTTAR_PRADESH = "Uttar Pradesh"
    UTTARAKHAND = "Uttarakhand"
    WEST_BENGAL = "West Bengal"
    ANDAMAN_AND_NICOBAR = "Andaman and Nicobar"
    LAKSHADWEEP = "Lakshadweep"
    DELHI = "Delhi"
    DADRA_HAVELI = "Dadra and Nagar Haveli and Daman & Diu"
    JAMMU_AND_KASHMIR = "Jammu and Kashmir"
    CHANDIGARH = "Chandigarh"
    LADAKH = "Ladakh"
    PUDUCHERRY = "Puducherry"
    UNKNOWN = "Unknown"


class ResourceType(Enum):
    ALLERGY_INTOLERANCE = "AllergyIntolerance"
    APPOINTMENT = "Appointment"
    MEDICATION_REQUEST = "MedicationRequest"
    MEDICATION_STATEMENT = "MedicationStatement"
    DOCUMENT_REFERENCE = "DocumentReference"
    OBSERVATION = "Observation"
    PATIENT = "Patient"
    BINARY = "Binary"
    BUNDLE = "Bundle"
    CARE_PLAN = "CarePlan"
    COMPOSITION = "Composition"
    CONDITION = "Condition"
    ENCOUNTER = "Encounter"
    FAMILY_MEMBER_HISTORY = "FamilyMemberHistory"
    IMAGING_STUDY = "ImagingStudy"
    IMMUNIZATION = "Immunization"
    IMMUNIZATION_RECOMMENDATION = "ImmunizationRecommendation"
    MEDIA = "Media"
    ORGANIZATION = "Organization"
    PRACTITIONER = "Practitioner"
    PRACTITIONER_ROLE = "PractitionerRole"
    PROCEDURE = "Procedure"
    SERVICE_REQUEST = "ServiceRequest"
    SPECIMEN = "Specimen"
    STAFF = "Staff"
    CONSENT = "Consent"
    CARE_CONTEXT = "CareContext"
    HIU_HEALTH_BUNDLE = "HiuHealthBundle"
    LOCATION = "Location"
    COVERAGE = "Coverage"
    COVERAGE_ELIGIBILITY_REQUEST = "CoverageEligibilityRequest"
    COVERAGE_ELIGIBILITY_RESPONSE = "CoverageEligibilityResponse"
    CLAIM = "Claim"
    CLAIM_RESPONSE = "ClaimResponse"
    COMMUNICATION_REQUEST = "CommunicationRequest"
    COMMUNICATION = "Communication"
    PAYMENT_NOTICE = "PaymentNotice"
    PAYMENT_RECONCILIATION = "PaymentReconciliation"
    TASK = "Task"
    INSURANCE_PLAN = "InsurancePlan"


class ConsentType(Enum):
    RECEIVED = "Received"
    REQUESTED = "Requested"


class Departments(Enum):
    UROLOGY = "urology"
    NEUROLOGY = "neurology"
    RADIOLOGY = "radiology"
    CARDIOLOGY = "cardiology"
    GENERAL_SURGERY = "general surgery"
    ENDOCRINOLOGY = "endocrinology"
    PEDIATRICS = "pediatrics"
    PATHOLOGY = "pathology"
    NEPHROLOGY = "nephrology"
    DERMATOLOGY = "dermatology"
    OTORHINOLARYNGOLOGY = "otorhinolaryngology"
    OPHTHALMOLOGY = "ophthalmology"
    EMERGENCY_MEDICINE = "emergency medicine"
    ORTHOPEDICS = "orthopedics"
    PSYCHIATRY = "psychiatry"
    ANESTHESIOLOGY = "anesthesiology"
    GASTROENTEROLOGY = "gastroenterology"
    INTENSIVE_CARE_MEDICINE = "intensive care medicine"
    FAMILY_MEDICINE = "family medicine"
    GYNAECOLOGY = "gynaecology"
    HEMATOLOGY = "hematology"


class Country(Enum):
    INDIA = "India"


class HealthFacilityType(Enum):
    HIP = "HIP"
    HIU = "HIU"


class OrganizationsIdType(Enum):
    ACCOUNT_ID = "accountId"
    ORGANIZATION_ID = "facilityId"
    ID = "id"


class AbhaLoginHint(str, Enum):
    ABHA_NUMBER = "abha-number"
    MOBILE = "mobile"
    EMAIL = "email"
    AADHAAR = "aadhaar"
    PASSWORD = "password"
    INDEX = "index"


class AuthMethodV2(str, Enum):
    AADHAAR_OTP = "AADHAAR_OTP"
    MOBILE_OTP = "MOBILE_OTP"
    PASSWORD = "PASSWORD"
    DEMOGRAPHICS = "DEMOGRAPHICS"
    AADHAAR_BIO = "AADHAAR_BIO"
    EMAIL_OTP = "EMAIL_OTP"


class VerifyAbhaLoginAuthResult(str, Enum):
    FAILED = "failed"
    SUCCESS = "success"


class PatientEndpoints:
    GET_ALL_PATIENTS = "/get/Patient"
    GET_PATIENT_BY_ID = "/get/Patient/{patient_id}"
    PATIENT_EXISTS = "/get/Patient/{patient_id}"
    CREATE_PATIENT = "/add/Patient"
    UPDATE_PATIENT = "/update/Patient"
    GET_PATIENT_BY_FILTERS = "/health-lake/get-profiles/Patient"
    DELETE_PATIENT = "/health-lake/delete/Patient/{patient_id}"


class PractitionerEndPoints:
    GET_ALL_PRACTITIONERS = "/get/Practitioner"
    GET_PRACTITIONER_BY_ID = "/get/Practitioner/{practitioner_id}"
    PRACTITIONER_EXISTS = "/get/Practitioner/{practitioner_id}"
    CREATE_PRACTITIONER = "/add/Practitioner"
    UPDATE_PRACTITIONER = "/update/Practitioner"
    GET_PRACTITIONER_BY_FILTERS = "/health-lake/get-profiles/Practitioner"
    DELETE_PRACTITIONER = "/health-lake/delete/Practitioner/{practitioner_id}"


class OrganizationEndPoints:
    GET_ALL_ORGANIZATIONS = "/facilities/"
    GET_ORGANIZATION_BY_ID = "/facilities/{search_param}/{search_term}"
    ORGANIZATION_EXISTS = "/facilities/{search_param}/{search_term}"
    REGISTER_ORGANIZATION = "/register-facility"
    UPDATE_ORGANIZATION = "/update-facility"
    SEARCH_ORGANIZATION = "/search-facility"
    DELETE_ORGANIZATION = "/facility/{organization_id}"


class UTILITY_API_ENDPOINTS:
    STATES_AND_DISTRICTS = "/lgd-states"
    SUBDISTRICTS = "/lgd-subdistricts?districtCode={district_code}"
    LOCATION = "https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={api_key}"
    OWNER_SUBTYPE = "/owner-subtype"
    SPECIALITIES = "/specialities"
    ORGANIZATION_TYPE = "/facility-type"
    ORGANIZATION_SUBTYPE = "/facility-subtypes"
    MASTER_TYPES = "/master-types"
    MASTER_DATA_BY_TYPE = "/master-data/{type}"


class DOCUMENT_LINKING_ENDPOINTS:
    GET_JSON_FROM_TEXT = "/gpt/extractive-summary"
    GET_SNOMED_CODES = "/search"


class GeneralInfoOptions(Enum):
    HAS_DIALYSIS_CENTER = "hasDialysisCenter"
    HAS_PHARMACY = "hasPharmacy"
    HAS_BLOOD_BANK = "hasBloodBank"
    HAS_CATH_LAB = "hasCathLab"
    HAS_DIAGNOSTIC_LAB = "hasDiagnosticLab"
    HAS_IMAGING_CENTER = "hasImagingCenter"


class AppointmentPriority(Enum):
    EMERGENCY = "Emergency"
    FOLLOW_UP_VISIT = "Follow-up visit"
    NEW = "New"


class AuthMode(Enum):
    MOBILE_OTP = "MOBILE_OTP"
    AADHAAR_OTP = "AADHAAR_OTP"
    DEMOGRAPHICS = "DEMOGRAPHICS"
    DIRECT = "DIRECT"


class CarePlanIntent(Enum):
    PROPOSAL = "proposal"
    PLAN = "plan"
    ORDER = "order"
    OPTION = "option"


class CarePlanStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ON_HOLD = "on-hold"
    REVOKED = "revoked"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"


class ClinicalStatus(Enum):
    ACTIVE = "active"
    RECURRENCE = "recurrence"
    RELAPSE = "relapse"
    INACTIVE = "inactive"
    REMISSION = "remission"
    RESOLVED = "resolved"


class DiagnosticReportStatus(Enum):
    REGISTERED = "registered"
    PARTIAL = "partial"
    PRELIMINARY = "preliminary"
    FINAL = "final"


class DosageFrequency(Enum):
    ONCE = "Once"
    TWICE = "Twice"
    THRICE = "Thrice"
    QUADTUPLE = "Quadtuple"


class MedicationRoute(Enum):
    ORAL = "Oral"
    TOPICAL = "Topical"
    INTRAVENOUS = "Intravenous"
    INTRAMUSCULAR = "IntraMuscular"
    SUBCUTANEOUS = "Subcutaneous"
    INHALATION = "Inhalation"
    INTRANASAL = "Intranasal"
    RECTAL = "Rectal"
    SUBLINGUAL = "Sublingual"
    BUCCAL = "Buccal"
    IV = "IntraVenal"


class MedicationMethod(Enum):
    SWALLOW = "Swallow"


class HealthInformationTypes(Enum):
    OPConsultation = "OPConsultation"
    Prescription = "Prescription"
    DischargeSummary = "DischargeSummary"
    DiagnosticReport = "DiagnosticReport"
    ImmunizationRecord = "ImmunizationRecord"
    HealthDocumentRecord = "HealthDocumentRecord"
    WellnessRecord = "WellnessRecord"


class ImmunizationStatusEnum(Enum):
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    NOT_DONE = "not-done"


class MedicationRequestStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ON_HOLD = "on-hold"
    REVOKED = "revoked"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"
    CANCELLED = "cancelled"


class MedicationStatementStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    INTENDED = "intended"
    STOPPED = "stopped"
    ON_HOLD = "on-hold"
    UNKNOWN = "unknown"
    NOT_TAKEN = "not-taken"


class ObservationStatus(Enum):
    REGISTERED = "registered"
    PRELIMINARY = "preliminary"
    FINAL = "final"
    AMENDED = "amended"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"


class ProcedureStatus(Enum):
    PREPARATION = "preparation"
    IN_PROGRESS = "in-progress"
    NOT_DONE = "not-done"
    ON_HOLD = "on-hold"
    STOPPED = "stopped"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"


class ServiceRequestStatus(Enum):
    PROPOSAL = "proposal"
    PLAN = "plan"
    DIRECTIVE = "directive"
    ORDER = "order"
    ORIGINAL_ORDER = "original-order"
    REFLEX_ORDER = "reflex-order"
    FILLER_ORDER = "filler-order"
    INSTANCE_ORDER = "instance-order"
    OPTION = "option"


class ServiceRequestIntent(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ON_HOLD = "on-hold"
    REVOKED = "revoked"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"


class VerificationStatus(Enum):
    UNCONFIRMED = "unconfirmed"
    CONFIRMED = "confirmed"
    REFUTED = "refuted"
    ENTERED_IN_ERROR = "entered-in-error"


TRANSFORM_SOURCE_TO_INTERMEDIATE_PROMPT = """
You are given patient data in a raw or unstructured format. Your task is, Follow these rules strictly and output a JSON object that adheres to the specified structure.

0. Common Transformation Rules for all sections:
   0.0. **Mandatory Output Fields:** The final JSON output MUST include ALL top-level keys specified in the example output structure (chiefComplaints, physicalExamination, conditions, medicalHistory, familyHistory, allergies, immunizations, currentMedications, investigationAdvice, prescribedMedications, procedures, advisoryNotes, followUps, opConsultDocuments). If there is no data for a field that expects a list (like conditions, medicalHistory, etc.), output an empty list `[]`. If there is no data for a field that expects an object (like physicalExaminations), output an object with its defined structure but with empty/null values where appropriate according to other rules. **Do not omit any top-level keys.**
   0.1. **Identify Date Information:** Carefully scan the given text to find any mention of a date or time period related to the event. This includes:
                *   Specific dates (e.g., "2020", "Jan 2020", "15-01-2020", "01/15/2020", "20-Mar-2019").
                *   Relative timeframes (e.g., "5 years ago", "6 months ago", "last week", "10 days ago", "one year back", "4 years back", "year back").
                *   **Extract/Calculate Year:**
                *   If a specific year is explicitly mentioned (e.g., "2020", "in 2019"), extract that year.
                *   If a full date is given (e.g., "15-01-2020", "03/20/2019"), extract the year part.
                *   If a relative timeframe is found (e.g., "5 years ago"),
                    calculate the approximate year by subtracting that duration from the **current year** (assume   the year the processing is happening).
                    For example, if processing occurs in 2024, "5 years ago"    resolves to the year 2019.
                    "6 months ago" or "10 days ago" would resolve to the current year.
                *   **Standardize Format:** Convert the extracted or calculated year into the strict `YYYY` format (e.g., "2019", "2020", "2024").
                *   **Handle Missing/Unclear Dates:** If no date information or year can be reliably extracted or calculated from the `given text,`,
                    set the `respective date` field to current date.


   0.2. **Determine Status (Active/Inactive Only):** Analyze the meaning of the relevant input text to determine if the item should be considered 'active' or 'inactive'.
        *   **Mapping Keywords and Context:**
            *   Map to **`"active"`** if the text implies ongoing relevance, current management, recurrence, relapse, in-progress, on-hold, intended, planned, scheduled, or uses explicit keywords like "active".
            *   Map to **`"inactive"`** if the text implies a past event, resolution, completion, failure, stoppage, not being done/taken, revocation, or uses explicit keywords like "inactive", "resolved", "completed", "stopped", "failed", "not-done", "revoked".
        *   **Inference:**
            *   Past events (e.g., "diagnosed X years ago", "done in YYYY", "surgery performed", "removed") usually imply **`"inactive"`**.
            *   Ongoing management or current relevance (e.g., "currently managed", "for [current condition]") usually implies **`"active"`**.
            *   Future actions (e.g., "planned", "scheduled") imply **`"active"`** (as an active plan/intention).
            *   Advice/Suggestions (e.g., "suggested", "advised") often imply **`"active"`** for the related condition/plan.
        *   **DEFAULT:** If no status can be reliably determined or mapped using the above, default the status field to **`"active"`**.
        *   **Output Format:** The value for any status field in the final JSON MUST be a single lowercase string, strictly either **`"active"`** or **`"inactive"`**. **DO NOT** output any other status values (like "completed", "resolved", etc.). **DO NOT** output a nested object like `{"status": "value"}`

1. Physical Examination Transformation Rules:

   1.1. **Target Field Name:** The output JSON object MUST contain a field named exactly `"physicalExamination"`. **This field must always be present**, even if the input lacks physical examination data, in which case it should follow Rule 1.6. # <-- Added explicit requirement
   1.2.  **Single Standardized Value and Unit:** For each measurement within `"physicalExamination"` 
          (e.g., `bloodPressure`, `heartRate`, `temperature`), the output MUST provide only a single `value` string and a single `unit` string, standardized as follows.
   1.3.  **Mandatory Unit Conversion:** The input value MUST be converted to the corresponding standard unit for the output. The required standard output units are:
         *   `bloodPressure`: Target unit is `"mmHg"`. (Convert from kPa if necessary: 1 kPa ≈ 7.50062 mmHg).
         *   `heartRate`: Target unit is `"bpm"`.
         *   `respiratoryRate`: Target unit is `"breaths/min"`.
         *   `temperature`: Target unit is `"°F"`. (Convert from °C if necessary: F = C * 9/5 + 32).
         *   `oxygenSaturation`: Target unit is `"%"` (Convert from fraction if necessary: % = fraction * 100).
         *   `height`: Target unit is `"cm"`. (Convert from ft/in or ft if necessary: 1 ft = 30.48 cm, 1 in = 2.54 cm).
         *   `weight`: Target unit is `"kg"`. (Convert from lbs if necessary: 1 lb ≈ 0.453592 kg).
   1.4.  **Input Processing:** Take the single `value` and `unit` provided in the input `physicalExaminations` for each measurement. 
          Perform the necessary unit conversion calculation based on the input unit to arrive at the value for the target standard unit specified in rule 1.3
   1.5.  **Output Value Formatting:** Ensure the output `value` is a clean string representation of the numerical result after conversion. 
          For blood pressure, round both the systolic and diastolic values to the nearest whole number (integer) 
          and maintain the "systolic/diastolic" format (e.g.,   convert "120.0/80.3" to "120/80").
   1.6.  **Handling Missing Data:** If a specific measurement is absent from the input, include its key in the output `"physicalExamination"` object with an empty string or null for `value` and the target `unit`. Example: `"height": {"value": "", "unit": "cm"}`. If the entire physical examination section is missing from the input, the output `"physicalExamination"` object MUST still be included, containing all measurement keys (bloodPressure, heartRate, etc.) with empty/null values and target units as specified here. # <-- Clarified handling for entirely missing section
   1.7.  **Structure Adherence:** Ensure the final output strictly follows the target JSON structure provided.

2. Medical History Transformation Rules:

    2.1. **Target Field Name:** The output JSON object MUST contain a field named exactly `"medicalHistory"`.

    2.2  **Input Processing:** The input `medicalHistory` is an array of objects. Each object might contain text descriptions under keys like `"condition"` and/or    `"procedure"`.

    2.3. **Item Granularity and Splitting:** Process each object in the input `medicalHistory` array. # <-- MODIFIED RULE 2.3
          *   If an input object contains **only** a `"condition"` key: Create exactly **one** output object using Structure 1 (Condition).
          *   If an input object contains **only** a `"procedure"` key: Create exactly **one** output object using Structure 2 (Procedure).
          *   If an input object contains **both** a `"condition"` key and a `"procedure"` key: Create exactly **two** separate output objects:
              *   One output object for the condition using Structure 1.
              *   One output object for the procedure using Structure 2.

    2.4. **Output Object Structure:** Each object in the output `medicalHistory` array MUST contain the following fields:
            *   Structure 1 (Condition): Contains `description` and `status`.
            *   Structure 2 (Procedure): Contains `procedureText`, `status`, `complicationText`, `performedDate`.


    2.5. **Field Population and Extraction:** For each identified medical event:
          **If the input object contains a "condition" key:** Create an output object containing:
           * `description`: **Identify and extract only the core medical condition name** from the input's `"condition"` key text (e.g., if the input is "Hypertension diagnosed 5 years ago (inactive)", extract just "Hypertension").
           * `status`: Apply **Rule 0.2** using the input's `"condition"` text. # <-- USE COMMON RULE
          *   **If the input object contains a "procedure" key:** Create an output object (Structure 2) containing:
              *   **PRIORITY 1:** Extract explicit status keywords (e.g., "(inactive)", "resolved", "active") found within the text.
              *   **PRIORITY 2 (Inference):** If no explicit keyword is found, infer the status from context (e.g., "diagnosed 5 years ago" usually implies 'inactive'; "currently managed" implies 'active').
              *   **DEFAULT (Last Resort):** Only if no status can be extracted or reasonably inferred, default this field to `"active"`.
         **If the input object contains a "procedure" key:** Create an output object containing:
          *  `procedureText`: Extract **only the core name or description** of the procedure itself from the input's `"procedure"` text (e.g., "Gallbladder removal surgery").
          *  `status`: Apply **Rule 0.2** using the input's `"procedure"` text. # <-- USE COMMON RULE
          *  `complicationText`: Extract any mentioned complications from the `"procedure"` text. If none mentioned or explicitly stated "without complications", set to empty string or null.
          *  `performedDate`: apply rule 0.1 by taking procedure as a input text and extract the correct year.

    2.6.  **Handling Missing Input:** If the input `medicalHistory` array is missing or empty, the output `medicalHistory` MUST be an empty array `[]`.

    2.7.  **Structure Adherence:** Ensure the final output strictly follows the target JSON structure provided for `medicalHistory` and its nested objects, including all required fields within each object.

3. Family History Transformation Rules:

    3.1.  **Target Field Name:** The output JSON object MUST contain a field named exactly `"familyHistory"`.

    3.2.  **Input Processing:** The input for family history is expected to be a text string (e.g., "Father had diabetes (status: active)").

    3.3.  **Output Object Structure:** The output `"familyHistory"` object MUST contain the following fields: `relation`, `healthNote`, `status`.

    3.4.  **Field Population and Extraction:**
          *   `relation`: Identify and extract the family relationship mentioned in the input text (e.g., "Father", "Mother", "Sister", "Brother", "Grandmother", etc.). Populate the `relation` field with this extracted relationship.
          *   `healthNote`: Identify and extract the medical condition(s) or health details described for the relative in the input text. Exclude the relationship itself and any explicit status indicators (like "(status: active)"). 
            Populate the `healthNote` field with this extracted description (e.g., "had diabetes", "history of heart attack").
          *  `status`: Look for an explicit status mentioned in the input text, often in parentheses (e.g., "(status: active)", "(deceased)"). Extract this status. If no status is explicitly mentioned in the text, default the `status` field to `"active"`.

    3.5.  **Handling Missing Input:** If the input text for family history is missing, empty, or does not contain identifiable information, 
          the output `"familyHistory"` object should still be present but contain empty strings or null values for `relation`, `healthNote`, and `status`. Example: `"familyHistory": {"relation": "", "healthNote": "", "status": ""}`.

    3.6.  **Structure Adherence:** Ensure the final output strictly follows the target JSON structure provided for the `familyHistory` field.

4. `allergies` Transformation Rules:

    4.1. Analyze the allergy string and set correct values for each field in this section.

    4.2  `status`: Apply **Rule 0.2** using the input allergy text. # <-- USE COMMON RULE

    4.3  `verificationStatus` : "confirmed" | "unconfirmed",
         * "confirmed" - This field indicates the level of certainty or verification of the allergy or intolerance.
         * "unconfirmed" - There is some suspicion of an allergy or intolerance, but it has not been definitively confirmed
         * if there is no information about `verificationStatus` assign default value as "confirmed"

    4.4 `recordedDate` : This field represents the date when the allergy or intolerance was recorded in the patient's medical record.
      Apply **Rule 0.1** by taking the allergy text as input to extract the correct year. **Ensure Rule 0.1's default behavior (setting to current date if no date is found) is applied.**

    4.5 `reaction`: This field describes the type of reaction the patient experiences when exposed to the allergen.
         This is a free-text field where the specific symptoms or manifestations of the allergic reaction are described.
         Examples might include "hives," "anaphylaxis," "rash," "swelling," etc.

5. `immunizations` Transformation Rules:

   5.1 * Analyze the input immunization string and set correct value to each field in output immunizations.

   5.2 `status`: Apply **Rule 0.2** using the input immunization text. Default to "completed" if Rule 0.2 results in "active" (as "active" isn't typical for immunizations). # <-- USE COMMON RULE + Adjustment

   5.3 `brandName` : The commercial name or brand name of the vaccine that was administered (e.g., "Covishield," "Pfizer-BioNTech").

   5.4 `vaccineName: A human-readable description of the vaccine (e.g., "Influenza vaccine").

   5.5 `vaccinatedDate`: This is the year when immunization was administered.
        Apply rule 0.1 to extract the `vaccinatedDate` by taking the immunization string as input text. **If no date information (specific date, year, or relative timeframe like 'X years ago') is found in the current medication text, `vaccinatedDate` MUST be set to an empty string or null.** Do not default to the current year.

   5.6 `lotNumber`: The lot number or batch number of the vaccine. It will be prefixed with "Lot number:" or a similar identifier.

   5.7 `expirationDate`: This is expiration date of the vaccine lot, Apply rule 0.1 to extract the `expirationDate` by taking the immunization string as input text. **If no date information (specific date, year, or relative timeframe like 'X years ago') is found in the current medication text, `expirationDate` MUST be set to an empty string or null.** Do not default to the current year.

  6. Current Medications Transformation Rules:

   6.1 `status`: Apply **Rule 0.2** using the input current medication text. # <-- USE COMMON RULE

   6.2 `dateAsserted`: The date when the medication statement was recorded or asserted.
        Apply rule 0.1 to extract the `dateAsserted` by taking the currentMedications string as input text. **If no date information (specific date, year, or relative timeframe like 'X years ago') is found in the current medication text, `dateAsserted` MUST be set to an empty string or null.** Do not default to the current year. 

   6.3 `medication`:  A  human-readable description  of  the  medication (e.g., "Metformin").Identifies the specific medication being taken.

   6.4 `reason`: Basically this a reason why the patient is taking the medication.The reason is typically provided in the string after "for" or "reason:".

7.Conditions Transformation Rules:

  7.0. **Target Field Name:** The output JSON object MUST contain a field named exactly `"conditions"`. If no relevant conditions are found in the input, this field MUST be present as an empty list `[]`. # <-- Added explicit requirement

  7.1 `description`: Extract the human-readable condition/disease name.

  7.2 `status`: Apply **Rule 0.2** using the input condition text. # <-- USE COMMON RULE
	
	Rule:
	Extract the first matching keyword or mapped status, converting it to lowercase.
	If no recognized status or mapping is found, default to: "status": "active".


8.Investigation Advice Transformation Rules:

  8.1 `description`: Extract the each human-readable test or investigation.

  8.2 `status`: IApply **Rule 0.2** using the input investigation advice text. # <-- USE COMMON RULE
	
  8.3 intent: Indicates the clinical purpose of the investigation advice.

	** Use "order" if the test is advised or suggested.

	** Use "plan" if the test is scheduled or planned for the future.

	** Use "follow-up" if the test has already been done but results are pending, or if explicitly mentioned as a follow-up.

	If multiple cues exist, select based on the first clearly stated context.

9.Prescribed Medication Transformation Rules:
  
  9.1  `status`: Apply **Rule 0.2** using the input prescribed medication text. # <-- USE COMMON RULE

  9.2 `authoredOn`: The date when the medication was recorded or asserted.
        apply rule 0.1 to extract the `dateAsserted` by taking prescribedMedications string as input text

  9.3 dosageDuration: Extract the numeric duration of medication use in days.

	* If the text says "5 days", return 5.

	* If it says "two weeks", return 14.

	* If it says "a month" or "for a month", return 30.

	* Convert common number words (e.g., "fifteen", "seven") into digits.

	* If no clear duration is found, set to 0.

  9.4 dosageFrequency: Extract the precise frequency in standard terms.

	Normalize expressions like:

	* "once a day" → "once daily"

	* "twice a day" or "2 times a day" → "twice daily"

	* "thrice a day" → "three times daily"

	* "every 8 hours" → "every 8 hours"

	Use the first clearly understood frequency phrase from the text.

	If no frequency is mentioned, use an empty string "".

  9.5 `medicationRoute`: 

	* Identify the route of administration of the medication from the text.(example :- "oral", "IV", "topical", or "inhalation")
	* Extract the exact word and use it as the value for medicationRoute.
	* If no route is mentioned, leave it as an empty string "".

  9.6 `medicationMethod` (based on route): Determine the method of intake based on the medicationRoute.

      oral → "swallow"

      IV → "inject"

      topical → "apply"

      inhalation → "inhale"

      If the route is not recognized or missing, leave medicationMethod as an empty string "".


  9.7 `medication`: Extract full name and strength of the medicine(e.g., "Amoxicillin 250 mg").
      * Ensure that there is a space between the numerical value and the unit (e.g., 250 mg, not 250mg).

  9.8 `reason`: Extract reason for use (e.g., "for fever" → "Fever").

10. Procedures Transformation Rules:

    10.1. **Target Field Name:** The output JSON object MUST contain a field named exactly `"procedures"`.
    10.2. **Input Processing:** The input is an array named `"currentProcedures"`. Each object in this array contains `"description"` and optionally `"complications"`.
    10.3. **Item Granularity:** Each object in the input `"currentProcedures"` array MUST result in exactly **one** corresponding object in the output `"procedures"` array.
    10.4. **Output Object Structure:** Each object in the output `"procedures"` array MUST contain the following fields: `procedureText`, `status`, `complicationText`, `performedDate`.
    10.5. **Field Population and Extraction:** For each input procedure object:
          *   `procedureText`: Extract **only the core name or description** of the procedure itself from the input's `"description"` text (e.g., if input is "Gallbladder removal surgery (Cholecystectomy)", extract just "Gallbladder removal surgery").
          *   `status`: Apply **Rule 0.2** using the input's `"description"` text to determine the status (e.g., "removal surgery" implies "completed").
          *   `complicationText`: Use the value from the input's `"complications"` key. If the key is missing or the value is "None", set this field to an empty string or null.
          *   `performedDate`: Apply **Rule 0.1** using the input's `"description"` text to extract/calculate the year (YYYY format). Set to empty string or null if no date is found.
    10.6. **Handling Missing Input:** If the input `"currentProcedures"` array is missing or empty, the output `"procedures"` MUST be an empty array `[]`.
    10.7. **Structure Adherence:** Ensure the final output strictly follows the target JSON structure provided for `procedures`.

11. Advisory Notes Transformation Rules:

    11.1. **Target Field Name:** The output JSON object MUST contain a field named exactly `"advisoryNotes"`.
    11.2. **Input Processing:** The input is an array named `"advisoryNotes"` containing strings. Each string might represent a piece of advice, potentially prefixed with a category.
    11.3. **Item Granularity:** Each string in the input `"advisoryNotes"` array MUST result in exactly **one** corresponding object in the output `"advisoryNotes"` array.
    11.4. **Output Object Structure:** Each object in the output `"advisoryNotes"` array MUST contain the following fields: `category`, `note`.
    11.5. **Field Population and Extraction:** For each input advisory note string: # <-- MODIFIED RULE 11.5
          *   `note`: Extract the main advisory text. If the string contains a ": " (colon followed by space), extract the part *after* it. If no ": " is present, use the entire input string as the note.
          *   `category`: assign a default value like "General Advice".
    11.6. **Handling Missing Input:** If the input `"advisoryNotes"` array is missing or empty, the output `"advisoryNotes"` MUST be an empty array `[]`.
    11.7. **Structure Adherence:** Ensure the final output strictly follows the target JSON structure provided for `advisoryNotes`.

12. Follow-Up Transformation Rules: # <-- NEW SECTION

    12.1. **Target Field Name:** The output JSON object MUST contain a field named exactly `"followUps"`.
    12.2. **Input Processing:** The input is an array named `"followUp"` containing strings describing follow-up instructions.
    12.3. **Item Granularity:** Each string in the input `"followUp"` array MUST result in exactly **one** corresponding object in the output `"followUps"` array.
    12.4. **Output Object Structure:** Each object in the output `"followUps"` array MUST contain the following fields: `serviceCategory`, `serviceType`, `appointmentType`, `appointmentReference`.
    12.5. **Field Population and Extraction:** For each input follow-up string:
          *   `serviceCategory`: Choose from "Outpatient", "Inpatient", or "Emergency" based on keywords in the text:
              *   "OP" / "OPD" → "Outpatient"
              *   "IP" / "IPD" / "admitted" → "Inpatient"
              *   "Emergency" / "ER" / "casualty" → "Emergency"
              *   If none match, set to empty string or null.
          *   `appointmentType`: Choose from "Consultation", "Review", or "Follow-up":
              *   Use "Review" for re-evaluation or checking treatment response.
              *   Use "Follow-up" for revisits or continued care (often implied by "visit after X days").
              *   If unclear, default to "Follow-up".
          *   `appointmentReference`:
              *   Extract any unique appointment identifier that appears to be a reference number, only if explicitly mentioned.
              *   Look for common patterns such as "OP-" or "IP-" followed by digits (e.g., OP-12345, IP-56789).
              *   If no reference is found, set to empty string or null.
    12.6. **Handling Missing Input:** If the input `"followUp"` array is missing or empty, the output `"followUps"` MUST be an empty array `[]`.
    12.7. **Structure Adherence:** Ensure the final output strictly follows the target JSON structure provided for `followUps`.

input json object:

{
        "chiefComplaints": "string",
        "physicalExamination": {
          "bloodPressure": { "value": "string", "unit": "string" },
          "heartRate": { "value": "string", "unit": "string" },
          "respiratoryRate": { "value": "string", "unit": "string" },
          "temperature": { "value": "string", "unit": "string" },
          "oxygenSaturation": { "value": "string", "unit": "string" },
          "height": { "value": "string", "unit": "string" },
          "weight": { "value": "string", "unit": "string" }
        },
        "medicalHistory": [
          {
            "condition": "string",
            "procedure": "string"
          }
        ],
        "familyHistory": [
          {
            "relation": "string",
            "healthNote": "string",
            "condition": "string"
          }
        ],
        "allergies": [
          "string"
        ],
        "immunizations": [
          "string"
        ],
        "conditions": [
          "string",
        ],
        "currentMedications": [
          "string"
        ],
        "investigationAdvice": [
          "string"
        ],
        "prescribedMedications": [
          "string"
        ],
        "currentProcedures": [
          {
            "description": "string",
            "complications": "string"
          }
        ],
        "advisoryNotes": [
          "string",
        ],
        "followUp": [
          "string"
        ],
        "opConsultDocument": [
          "string"
        ]
      }
    }

output json object:

{
  "chiefComplaints": "string",
  "physicalExamination": {
    "bloodPressure": {"value": "string", "unit": "string"},
    "heartRate": {"value": "string", "unit": "string"},
    "respiratoryRate": {"value": "string", "unit": "string"},
    "temperature": {"value": "string", "unit": "string"},
    "oxygenSaturation": {"value": "string", "unit": "string"},
    "height": {"value": "string", "unit": "string"},
    "weight": {"value": "string", "unit": "string"}
  },
  "conditions": [
    {
      "description": "string",
      "status": "string"
    }
  ],
  "medicalHistory": [
    {
      "description": "string",
      "status": "string",
    }
    {
     "procedureText": "string",
      "status": "string",
      "complicationText": "string",
      "performedDate": "string"
      }
  ],
  "familyHistory": [{
    "relation": "string",
    "healthNote": "string",
    "status": "string"
  }],
  "allergies": [
    {
      "status": "string",
      "verificationStatus": "string",
      "recordedDate": "string",
      "reaction": "string"
    }
  ],
  "immunizations": [
    {
      "status": "string",
      "brandName": "string",
      "vaccineName": "string",
      "vaccinatedDate": "string",
      "lotNumber": "string",
      "expirationDate": "string"
    }
  ],
  "currentMedications": [
    {
      "status": "active",
      "date Asserted": "2025",
      "medication": "Amlodipine 5mg",
      "reason": "Hypertension"
    }
  ],
  "investigationAdvice": [
    { 
      "description": "string",
      "status": "string",
      "intent": "string"
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
      "reason": "string"
    }
  ],
  "procedures": [
    {
      "status": "string",
      "procedureText": "string",
      "complicationText": "string",
      "performedDate": "string"
    }
  ],
  "advisoryNotes": [
    {
      "category": "string",
      "note": "string"
    }
  ],
  "followUps": [
    {
      "serviceCategory": "string",
      "serviceType": "Consultation",
      "appointmentType": "string",
      "appointmentReference": "string"
    }
  ],
  "opConsultDocuments": [
    {
      "base64File": "string"
    }
  ]
}
"""
VITALS_REFERENCE_RANGES = {
    "bloodPressure": {
        "mmHg": {
            "systolic": {"low": 90, "high": 120},
            "diastolic": {"low": 60, "high": 80},
        }
    },
    "heartRate": {"bpm": {"low": 60, "high": 100}},
    "respiratoryRate": {"breaths/min": {"low": 12, "high": 20}},
    "temperature": {
        "°F": {"low": 97.0, "high": 99.5},
        "°C": {"low": 36.1, "high": 37.5},
    },
    "oxygenSaturation": {"%": {"low": 95, "high": 100}},
    "height": {
        "cm": {"low": 140, "high": 200},
        "m": {"low": 1.4, "high": 2.0},
        "in": {"low": 55, "high": 79},
    },
    "weight": {"kg": {"low": 40, "high": 120}, "lb": {"low": 88, "high": 265}},
}
