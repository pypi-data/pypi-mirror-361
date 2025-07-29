"""
This module defines data models using Pydantic for validating and
structuring API request and response data.
"""

import re
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

from carestack.common.enums import (
    Departments,
    Gender,
    ResourceType,
    StatesAndUnionTerritories,
)

VALIDATION_MSGS = {
    "registration_id": "registrationId cannot be empty.",
    "first_name": "Must be at least 3 characters long and contain only letters and dots.",
    "last_name": "Must be at least 3 characters long and contain only letters and dots.",
    "mobile_number": "Invalid format. Expected +91 followed by 10 digits.",
    "emailId": "Invalid email format.",
    "address": "Must be at least 5 characters long.",
    "pincode": "Invalid format. Expected 6 digits.",
    "idType": "Invalid idType.",
    "patient_type": "Invalid patientType.",
    "gender": "Invalid gender.",
    "state": "Invalid state.",
    "resource_type": "Invalid resourceType.",
    "birth_date": "Invalid format. Expected YYYY-MM-DD.",
    "organization": "Must be a string.",
    "count": "Must be a string.",
    "identifier": "Must be a string.",
    "designation": "designation cannot be empty.",
    "status": "status cannot be empty.",
    "joining_date": "joiningDate cannot be empty.",
    "staff_type": "staffType cannot be empty.",
}

PractitionerEntry = TypeVar("PractitionerEntry")


class Link(BaseModel):
    """
    Represents a pagination link in a response, typically used for handling
    the next page in paginated data.

    Attributes:
        next_page (str, optional): The URL or link to the next page in a paginated list.

    Configuration:
        model_config: Configuration settings to enable population by name and
        use enum values for the model fields.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    next_page: Optional[str] = Field(None, alias="nextPage")


class PractitionerFilterResponse(BaseModel, Generic[PractitionerEntry]):
    """
    Represents the response containing a list of practitioners, along with pagination
    information and the total count.

    Attributes:
        entry (list[PractitionerEntry]): A list of practitioner entries in the response.
        link (Link, optional): A link object that contains the URL for the next page in
                                the paginated list, if available.
        total (int, optional): The total number of practitioners available in the dataset.

    Configuration:
        model_config: Configuration settings to enable population by name and use
                      enum values for the model fields.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    entry: list[PractitionerEntry]
    link: Optional[Link] = None
    total: Optional[int] = None


class GetPractitionerResponse(BaseModel):
    """
    DTO for representing the response when getting one or more practitioners.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    type: Optional[str] = None
    message: Optional[str] = None
    request_resource: Optional[Any] = Field(None, alias="requestResource")
    total_number_of_records: Optional[int] = Field(None, alias="totalNumberOfRecords")
    next_page_link: Optional[str] = Field(None, alias="nextPageLink")


class CreateUpdatePractitionerResponse(BaseModel):
    """
    DTO for representing the response after creating or updating a practitioner.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    type: Optional[str] = None
    message: Optional[str] = None
    resource_id: Optional[str] = Field(None, alias="resourceId")


class PractitionerBaseDTO(BaseModel):
    """
    Base DTO for practitioner data with common validations.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    registration_id: str = Field(..., alias="registrationId")
    department: str
    designation: str
    status: str
    joining_date: str = Field(..., alias="joiningDate")
    staff_type: str = Field(..., alias="staffType")
    first_name: str = Field(..., alias="firstName")
    middle_name: Optional[str] = Field(None, alias="middleName")
    last_name: Optional[str] = Field(None, alias="lastName")
    birth_date: Optional[str] = Field(None, alias="birthDate")
    gender: str
    mobile_number: Optional[str] = Field(None, alias="mobileNumber")
    email_id: Optional[str] = Field(None, alias="emailId")
    address: str
    pincode: Optional[str] = None
    state: Optional[str]
    wants_to_link_whatsapp: Optional[bool] = Field(None, alias="wantsToLinkWhatsapp")
    photo: Optional[str] = None
    resource_type: str = Field(..., alias="resourceType")
    resource_id: Optional[str] = Field(None, alias="resourceId")

    @field_validator("registration_id")
    @classmethod
    def validate_registration_id(cls, value: str) -> str:
        """
        Validates the registration ID value.

        Ensures that the registration ID is not empty. If the value is empty,
        a ValueError is raised with a specific error message.

        Args:
            cls: The class the method belongs to (used in class methods).
            value (str): The registration ID to validate.

        Raises:
            ValueError: If the registration ID is empty.

        Returns:
            str: The validated registration ID.
        """
        if not value:
            raise ValueError(VALIDATION_MSGS["registration_id"])
        return value

    @field_validator("department")
    @classmethod
    def validate_department(cls, value: str) -> str:
        """
        Validates the department value.

        Ensures that the department is valid by checking if it exists in the predefined
        list of departments. If the department value is not found, a ValueError is raised
        with a specific error message.

        Args:
            cls: The class the method belongs to (used in class methods).
            value (str): The department to validate.

        Raises:
            ValueError: If the department is not in the predefined list of valid departments.

        Returns:
            str: The validated department value.
        """
        if value is not None and value not in [e.value for e in Departments]:
            raise ValueError(VALIDATION_MSGS["department"])
        return value

    @field_validator("designation")
    @classmethod
    def validate_designation(cls, value: str) -> str:
        """
        Validates the designation value.

        Args:
            cls: The class to which this method belongs (used for class methods).
            value (str): The designation value to be validated.

        Raises:
            ValueError: If the designation value is empty or None.

        Returns:
            str: The validated designation value if it is not empty.
        """
        if not value:
            raise ValueError(VALIDATION_MSGS["designation"])
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        """
        Validates the status value.

        Args:
            cls: The class to which this method belongs (used for class methods).
            value (str): The status value to be validated.

        Raises:
            ValueError: If the status value is empty or None.

        Returns:
            str: The validated status value if it is not empty.
        """
        if not value:
            raise ValueError(VALIDATION_MSGS["status"])
        return value

    @field_validator("joining_date")
    @classmethod
    def validate_joining_date(cls, value: str) -> str:
        """
        Validates the joining date value.

        Args:
            cls: The class to which this method belongs (used for class methods).
            value (str): The joining date to be validated.

        Raises:
            ValueError: If the joining date is empty or None.

        Returns:
            str: The validated joining date if it is not empty.
        """
        if not value:
            raise ValueError(VALIDATION_MSGS["joining_date"])
        return value

    @field_validator("staff_type")
    @classmethod
    def validate_staff_type(cls, value: str) -> str:
        """
        Validates the staff type value.

        Args:
            cls: The class to which this method belongs (used for class methods).
            value (str): The staff type to be validated.

        Raises:
            ValueError: If the staff type is empty or None.

        Returns:
            str: The validated staff type if it is not empty.
        """
        if not value:
            raise ValueError(VALIDATION_MSGS["staff_type"])
        return value

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, value: str) -> str:
        """
        Validates the first name to ensure it only contains alphabetic characters and dots.

        Args:
            cls: The class to which this method belongs (used for class methods).
            value (str): The first name to be validated.

        Raises:
            ValueError: If the first name contains invalid characters (i.e., anything other than letters or dots).

        Returns:
            str: The validated first name if it contains only valid characters.
        """
        if not re.fullmatch(r"^[a-zA-Z.]+$", value):
            raise ValueError(VALIDATION_MSGS["first_name"])
        return value

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, value: Optional[str]) -> Optional[str]:
        """
        Validates the last name to ensure it only contains alphabetic characters and dots.

        Args:
            cls: The class to which this method belongs (used for class methods).
            value (Optional[str]): The last name to be validated. It can be None.

        Raises:
            ValueError: If the last name contains invalid characters (i.e., anything other than letters or dots).

        Returns:
            Optional[str]: The validated last name if it contains only valid characters, or None if no value is provided.
        """
        if value and not re.fullmatch(r"^[a-zA-Z.]+$", value):
            raise ValueError(VALIDATION_MSGS["last_name"])
        return value

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, value: Optional[str]) -> Optional[str]:
        """
        Validates the pincode to ensure it matches the format of exactly 6 digits.

        Args:
            cls: The class to which this method belongs (used for class methods).
            value (Optional[str]): The pincode to be validated. It can be None.

        Raises:
            ValueError: If the pincode does not match the required 6-digit format.

        Returns:
            Optional[str]: The validated pincode if it matches the required format, or None if no value is provided.
        """
        if value and not re.fullmatch(r"^\d{6}$", value):
            raise ValueError(VALIDATION_MSGS["pincode"])
        return value

    @field_validator("mobile_number")
    @classmethod
    def validate_mobile_number(cls, value: Optional[str]) -> Optional[str]:
        """
        Validates the mobile number to ensure it follows the format of +91 followed by 10 digits.

        Args:
            cls: The class to which this method belongs (used for class methods).
            value (Optional[str]): The mobile number to be validated. It can be None.

        Raises:
            ValueError: If the mobile number does not match the required format (+91 followed by 10 digits).

        Returns:
            Optional[str]: The validated mobile number if it matches the required format, or None if no value is provided.
        """
        if value is not None and not re.fullmatch(r"^\+91\d{10}$", value):
            raise ValueError(VALIDATION_MSGS["mobile_number"])
        return value

    @field_validator("birth_date")
    @classmethod
    def validate_birthdate(cls, value: str) -> str:
        """
        Validates the birthdate to ensure it follows the format YYYY-MM-DD.

        Args:
            cls: The class to which this method belongs (used for class methods).
            value (str): The birthdate to be validated. It should be a string in the format YYYY-MM-DD.

        Raises:
            ValueError: If the birthdate does not match the required format or is invalid.

        Returns:
            str: The validated birthdate if it matches the required format, or the original value if no validation is needed.
        """
        if value:
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError as exc:
                raise ValueError(VALIDATION_MSGS["birth_date"]) from exc
        return value

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value: str) -> str:
        """
        Validates the gender value against the Gender enum.

        Args:
            value (str): The gender value to validate.

        Raises:
            ValueError: If the value is not a valid gender.

        Returns:
            str: The validated gender value.
        """
        if value.lower() not in [e.value for e in Gender]:
            raise ValueError(VALIDATION_MSGS["gender"])
        return value

    @field_validator("address")
    @classmethod
    def validate_address(cls, value: str) -> str:
        """
        Validates the address value.

        Args:
            value (str): The address to validate.

        Raises:
            ValueError: If the address is empty.

        Returns:
            str: The validated address value.
        """
        if not value:
            raise ValueError(VALIDATION_MSGS["address"])
        return value

    @field_validator("state")
    @classmethod
    def validate_state(cls, value: Optional[str]) -> Optional[str]:
        """
        Validates the state value against the predefined list of states and union territories.

        Args:
            value (Optional[str]): The state name to validate.

        Raises:
            ValueError: If the provided state is not in the predefined list.

        Returns:
            Optional[str]: The validated state value or None if no value is provided.
        """
        if value and value not in [e.value for e in StatesAndUnionTerritories]:
            raise ValueError(VALIDATION_MSGS["state"])
        return value

    @field_validator("resource_type")
    @classmethod
    def validate_resource_type(cls, value: str) -> str:
        """
        Validates the resource type against the predefined ResourceType enum.

        Args:
            value (str): The resource type to validate.

        Raises:
            ValueError: If the value is not a valid resource type.

        Returns:
            str: The validated resource type.
        """
        if value is not None and value not in [e.value for e in ResourceType]:
            raise ValueError(VALIDATION_MSGS["resource_type"])
        return value


class CreatePractitionerDTO(PractitionerBaseDTO):
    """
    DTO for creating a new practitioner (inherits validations from BaseDTO).
    """


class UpdatePractitionerDTO(PractitionerBaseDTO):
    """
    DTO for updating an existing practitioner (inherits validations from BaseDTO).
    """


class PractitionerFiltersDTO(BaseModel):
    """
    Data Transfer Object (DTO) for filtering Practitioner records.

    Attributes:
        first_name (Optional[str]): The practitioner's first name.
        last_name (Optional[str]): The practitioner's last name.
        birth_date (Optional[str]): The practitioner's birth date.
        gender (Optional[str]): The practitioner's gender.
        mobile_number (Optional[str]): The practitioner's mobile number.
        email_id (Optional[str]): The practitioner's email ID.
        count (Optional[int]): The number of records to fetch.
        state (Optional[str]): The practitioner's state.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    birth_date: Optional[str] = Field(None, alias="birthDate")
    gender: Optional[str] = None
    mobile_number: Optional[str] = Field(None, alias="mobileNumber")
    email_id: Optional[str] = Field(None, alias="emailId")
    count: Optional[int] = None
    state: Optional[str] = None
