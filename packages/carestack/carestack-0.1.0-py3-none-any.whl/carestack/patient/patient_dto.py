"""
This module defines data models using Pydantic for validating and
structuring API request and response data.
"""

import re
from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator

from carestack.common.enums import (
    Gender,
    PatientIdTypeEnum,
    PatientTypeEnum,
    ResourceType,
    StatesAndUnionTerritories,
)

PatientEntry = TypeVar("PatientEntry")

VALIDATION_MSGS = {
    "firstName": "Must be at least 3 characters long and contain only letters and dots.",
    "lastName": "Must be at least 3 characters long and contain only letters and dots.",
    "mobileNumber": "Invalid format. Expected +91 followed by 10 digits.",
    "emailId": "Invalid email format.",
    "address": "Must be at least 5 characters long.",
    "pincode": "Invalid format. Expected 6 digits.",
    "idType": "Invalid idType.",
    "patientType": "Invalid patientType.",
    "gender": "Invalid gender.",
    "state": "Invalid state.",
    "resourceType": "Invalid resourceType.",
    "birthDate": "Invalid format. Expected YYYY-MM-DD.",
    "organization": "Must be a string.",
    "count": "Must be a string.",
    "identifier": "Must be a string.",
}


class GetPatientResponse(BaseModel):
    """
    DTO for representing the response when getting one or more patients.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    type: Optional[str] = Field(default=None)
    message: Optional[str] = Field(default=None)
    request_resource: Optional[Any] = Field(None, alias="requestResource")
    total_number_of_records: Optional[int] = Field(None, alias="totalNumberOfRecords")
    next_page_link: Optional[str] = Field(None, alias="nextPageLink")


class Link(BaseModel):
    """
    Represents a pagination link in API responses.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )
    next_page: Optional[str] = Field(None, alias="nextPage")


class PatientFilterResponse(BaseModel, Generic[PatientEntry]):
    """
    A generic response model for filtering patient entries.

    This class is designed to handle API responses that return a list
    of patient-related data along with pagination links and total count.

    Attributes:
        entry (List[T]): A list of patient entries.
        link (Optional[Link]): Pagination link information (if available).
        total (Optional[int]): Total number of patients (if provided).
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )
    entry: List[PatientEntry]
    link: Optional[Link] = None
    total: Optional[int] = None


class CreateUpdatePatientResponse(BaseModel):
    """
    DTO for representing the response after creating or updating a patient.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )
    type: Optional[str] = Field(default=None)
    message: Optional[str] = Field(default=None)
    resource_id: Optional[str] = Field(None, alias="resourceId")
    validation_errors: Optional[list[Any]] = Field(None, alias="validationErrors")
    resource: Optional[dict[str, Any]] = None


class PatientDTO(BaseModel):
    """
    DTO for creating a new patient (inherits validations from BaseDTO).
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )
    id_number: str = Field(..., alias="idNumber")
    id_type: str = Field(..., alias="idType")
    abha_address: Optional[str] = Field(None, alias="abhaAddress")
    patient_type: str = Field(..., alias="patientType")
    first_name: str = Field(..., alias="firstName")
    middle_name: Optional[str] = Field(None, alias="middleName")
    last_name: Optional[str] = Field(None, alias="lastName")
    birth_date: str = Field(..., alias="birthDate")
    gender: str
    mobile_number: Optional[str] = Field(None, alias="mobileNumber")
    email_id: Optional[str] = Field(None, alias="emailId")
    address: str
    pincode: Optional[str] = None
    state: Optional[str] = None
    wants_to_link_whatsapp: Optional[bool] = Field(None, alias="wantsToLinkWhatsapp")
    photo: Optional[str] = None
    resource_type: str = Field(..., alias="resourceType")
    resource_id: Optional[str] = Field(None, alias="resourceId")

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, value: str) -> str:
        """
        Validates the first name.

        Ensures the first name is at least 3 characters long and
        contains only letters (a-z, A-Z) and dots ('.').

        Args:
            value (str): The first name to validate.

        Returns:
            str: The validated first name.

        Raises:
            ValueError: If the first name is too short or contains invalid characters.
        """
        if len(value) < 3:
            raise ValueError(VALIDATION_MSGS["firstName"])
        if not re.fullmatch(r"^[a-zA-Z.]+$", value):
            raise ValueError(VALIDATION_MSGS["firstName"])
        return value

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, value: str) -> str:
        """
        Validates the last name.

        Ensures that if a last name is provided, it must be at least 3 characters long
        and contain only letters (a-z, A-Z) and dots ('.').

        Args:
            value (str): The last name to validate.

        Returns:
            str: The validated last name.

        Raises:
            ValueError: If the last name is too short or contains invalid characters.
        """
        if value and len(value) < 3:
            raise ValueError(VALIDATION_MSGS["lastName"])
        if value and not re.fullmatch(r"^[a-zA-Z.]+$", value):
            raise ValueError(VALIDATION_MSGS["lastName"])
        return value

    @field_validator("mobile_number")
    @classmethod
    def validate_mobile_number(cls, value: str) -> str:
        """
        Validates a mobile number.

        Ensures that the mobile number starts with "+91" and is followed by exactly 10 digits.

        Args:
            value (str): The mobile number to validate.

        Returns:
            str: The validated mobile number.

        Raises:
            ValueError: If the mobile number does not match the required format.
        """
        if value and not re.fullmatch(r"^\+91\d{10}$", value):
            raise ValueError(VALIDATION_MSGS["mobileNumber"])
        return value

    @field_validator("email_id")
    @classmethod
    def validate_email(cls, value: str) -> str:
        """
        Validates an email address.

        Ensures that the email address follows a valid format (i.e., contains "@" and a domain).

        Args:
            value (str): The email address to validate.

        Returns:
            str: The validated email address.

        Raises:
            ValueError: If the email address is not in a valid format.
        """
        if value and not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError(VALIDATION_MSGS["emailId"])
        return value

    @field_validator("address")
    @classmethod
    def validate_address(cls, value: str) -> str:
        """
        Validates the address field.

        Ensures that the address has a minimum length of 5 characters.

        Args:
            value (str): The address to validate.

        Returns:
            str: The validated address.

        Raises:
            ValueError: If the address length is less than 5 characters.
        """
        if len(value) < 5:
            raise ValueError(VALIDATION_MSGS["address"])
        return value

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, value: str) -> str:
        """
        Validates the pincode field.

        Ensures that the pincode is a 6-digit numeric string.

        Args:
            value (str): The pincode to validate.

        Returns:
            str: The validated pincode.

        Raises:
            ValueError: If the pincode is not exactly 6 digits.
        """
        if value and not re.fullmatch(r"^\d{6}$", value):
            raise ValueError(VALIDATION_MSGS["pincode"])
        return value

    @field_validator("id_type")
    @classmethod
    def validate_id_type(cls, value: str) -> str:
        """
        Validates the ID type.

        Ensures that the provided ID type is a valid value from the `PatientIdTypeEnum`.

        Args:
            value (str): The ID type to validate.

        Returns:
            str: The validated ID type.

        Raises:
            ValueError: If the ID type is not recognized.
        """
        if value is not None and value.upper() not in [
            e.value for e in PatientIdTypeEnum
        ]:
            raise ValueError(VALIDATION_MSGS["idType"])
        return value

    @field_validator("patient_type")
    @classmethod
    def validate_patient_type(cls, value: str) -> str:
        """
        Validates the patient type.

        Ensures that the provided patient type is a valid value from the `PatientTypeEnum`.

        Args:
            value (str): The patient type to validate.

        Returns:
            str: The validated patient type.

        Raises:
            ValueError: If the patient type is not recognized.
        """
        if value is not None and value.upper() not in [
            e.value for e in PatientTypeEnum
        ]:
            raise ValueError(VALIDATION_MSGS["patientType"])
        return value

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value: str) -> str:
        """
        Validates the gender field.

        Ensures that the provided gender value is a valid option from the `Gender` enum.

        Args:
            value (str): The gender value to validate.

        Returns:
            str: The validated gender value.

        Raises:
            ValueError: If the gender is not recognized.
        """
        if value is not None and value.lower() not in [e.value for e in Gender]:
            raise ValueError(VALIDATION_MSGS["gender"])
        return value

    @field_validator("state")
    @classmethod
    def validate_state(cls, value: str) -> str:
        """
        Validates the given state value.

        Ensures that the provided state exists in the `StatesAndUnionTerritories` enum.

        Args:
            value (str): The state value to validate.

        Returns:
            str: The validated state value.

        Raises:
            ValueError: If the state is not recognized.
        """
        if value is not None and value not in [
            e.value for e in StatesAndUnionTerritories
        ]:
            raise ValueError(VALIDATION_MSGS["state"])
        return value

    @field_validator("resource_type")
    @classmethod
    def validate_resource_type(cls, value: str) -> str:
        """
        Validates the given resource type.

        Ensures that the provided value matches the expected resource type
        (i.e., `ResourceType.PATIENT.value`).

        Args:
            value (str): The resource type to validate.

        Returns:
            str: The validated resource type.

        Raises:
            ValueError: If the resource type is not `PATIENT`.
        """
        if value != ResourceType.PATIENT.value:
            raise ValueError(VALIDATION_MSGS["resourceType"])
        return value

    @field_validator("birth_date")
    @classmethod
    def validate_birthdate(cls, value: str) -> str:
        """
        Validates the birthdate format.

        Ensures that the given date string follows the format 'YYYY-MM-DD'.

        Args:
            value (str): The birthdate string to validate.

        Returns:
            str: The validated birthdate string.

        Raises:
            ValueError: If the date format is incorrect.
        """
        if value:
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError as exc:
                raise ValueError(VALIDATION_MSGS["birthDate"]) from exc
        return value


class UpdatePatientDTO(BaseModel):
    """
    DTO for updating an existing patient with specific fields and validations.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )
    resource_id: str = Field(..., alias="resourceId")
    email_id: Optional[str] = Field(None, alias="emailId")
    mobile_number: Optional[str] = Field(None, alias="mobileNumber")
    resource_type: str = Field(..., alias="resourceType")

    @field_validator("mobile_number")
    @classmethod
    def validate_mobile_number(cls, value: str) -> str:
        """
        Validates the mobile number format.

        Ensures the mobile number follows the Indian format, starting with `+91` followed by 10 digits.
        Raises a ValueError if the format is incorrect.

        Args:
            value (str): The mobile number to validate.

        Returns:
            str: The validated mobile number.

        Raises:
            ValueError: If the mobile number format is invalid.
        """
        if value and not re.fullmatch(r"^\+91\d{10}$", value):
            raise ValueError(VALIDATION_MSGS["mobileNumber"])
        return value

    @field_validator("email_id")
    @classmethod
    def validate_email(cls, value: str) -> str:
        """
        Validates the email format.

        Ensures the email follows a valid format (e.g., `example@domain.com`).
        Raises a ValueError if the format is incorrect.

        Args:
            value (str): The email address to validate.

        Returns:
            str: The validated email address.

        Raises:
            ValueError: If the email format is invalid.
        """
        if value and not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError(VALIDATION_MSGS["emailId"])
        return value

    @field_validator("resource_type")
    @classmethod
    def validate_resource_type(cls, value: str) -> str:
        """
        Validates the resource type.

        Ensures that the provided resource type matches `ResourceType.PATIENT.value`.
        Raises a ValueError if the resource type is invalid.

        Args:
            value (str): The resource type to validate.

        Returns:
            str: The validated resource type.

        Raises:
            ValueError: If the resource type does not match `ResourceType.PATIENT.value`.
        """
        if value != ResourceType.PATIENT.value:
            raise ValueError(VALIDATION_MSGS["resourceType"])
        return value


class PatientFiltersDTO(BaseModel):
    """
    DTO for filtering patients.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    birth_date: Optional[str] = Field(None, alias="birthDate")
    gender: Optional[str] = None
    phone: Optional[str] = Field(None, alias="phone")
    state: Optional[str] = None
    organization: Optional[str] = None
    count: Optional[int] = None
    identifier: Optional[str] = None

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, value: str) -> str:
        """
        Validates the first name.

        Ensures that the first name is at least 3 characters long and
        contains only letters and dots.

        Args:
            value (str): The first name to validate.

        Returns:
            str: The validated first name.

        Raises:
            ValueError: If the first name is less than 3 characters
                        or contains invalid characters.
        """
        if value and len(value) < 3:
            raise ValueError("firstName must be at least 3 characters long")
        if value and not re.fullmatch("^[a-zA-Z.]+$", value):
            raise ValueError("firstName must only contain letters and dots")
        return value

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, value: str) -> str:
        """
        Validates the last name.

        Ensures that the last name is at least 3 characters long and
        contains only letters and dots.

        Args:
            value (str): The last name to validate.

        Returns:
            str: The validated last name.

        Raises:
            ValueError: If the last name is less than 3 characters
                        or contains invalid characters.
        """
        if value and len(value) < 3:
            raise ValueError("lastName must be at least 3 characters long")
        if value and not re.fullmatch("^[a-zA-Z.]+$", value):
            raise ValueError("lastName must only contain letters and dots")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        """
        Validates a phone number.

        Ensures that the phone number follows the format: +91 followed by 10 digits.

        Args:
            value (str): The phone number to validate.

        Returns:
            str: The validated phone number.

        Raises:
            ValueError: If the phone number does not match the required format.
        """
        if value and not re.fullmatch(r"^\+91\d{10}$", value):
            raise ValueError(
                "Invalid mobile number format. It should be +91 followed by 10 digits"
            )
        return value

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value: str) -> str:
        """
        Validates the gender value.

        Ensures that the provided gender is valid and exists in the Gender enum.

        Args:
            value (str): The gender to validate.

        Returns:
            str: The validated gender value.

        Raises:
            ValueError: If the gender is not valid (i.e., not in the Gender enum).
        """
        if value and value not in [e.value for e in Gender]:
            raise ValueError("Invalid gender")
        return value

    @field_validator("state")
    @classmethod
    def validate_state(cls, value: str) -> str:
        """
        Validates the state value.

        Ensures that the provided state is valid and exists in the StatesAndUnionTerritories enum.

        Args:
            value (str): The state to validate.

        Returns:
            str: The validated state value.

        Raises:
            ValueError: If the state is not valid (i.e., not in the StatesAndUnionTerritories enum).
        """
        if value is not None and value not in [
            e.value for e in StatesAndUnionTerritories
        ]:
            raise ValueError(f"Invalid state: {value}")
        return value

    @field_validator("birth_date")
    @classmethod
    def validate_birthdate(cls, value: str) -> str:
        """
        Validates the birthdate format.

        Ensures that the provided birthdate follows the format YYYY-MM-DD.

        Args:
            value (str): The birthdate string to validate.

        Returns:
            str: The validated birthdate.

        Raises:
            ValueError: If the birthdate format is invalid (i.e., not in the format YYYY-MM-DD).
        """
        if value:
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError as exc:
                raise ValueError(
                    "Invalid birthDate format. Expected YYYY-MM-DD"
                ) from exc
        return value


class BooleanResponse(BaseModel):
    success: bool
