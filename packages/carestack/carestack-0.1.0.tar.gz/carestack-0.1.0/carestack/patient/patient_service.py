"""Patient services.
This module provides functionalities for creating, updating, and deleting
patient in the system.
"""

import json
import logging
from typing import Any, Optional, Type

from pydantic import BaseModel, ValidationError

from carestack.base.base_service import BaseService
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import PatientEndpoints
from carestack.patient.patient_dto import (
    BooleanResponse,
    CreateUpdatePatientResponse,
    GetPatientResponse,
    PatientDTO,
    PatientFilterResponse,
    PatientFiltersDTO,
    UpdatePatientDTO,
)


class Patient(BaseService):
    """
    SDK-friendly PatientService for managing patient-related operations.

    This class provides methods for interacting with patient records, including retrieval,
    creation, updating, and deletion.

    Args:
        config (ClientConfig): Configuration object containing API credentials and settings.
    """

    def __init__(self, config: ClientConfig) -> None:
        super().__init__(config)
        self.logger = logging.getLogger(__name__)

    async def __validate_data(
        self, dto_type: Type[BaseModel], request_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Validates request data using Pydantic models.

        Args:
            dto_type (BaseModel): Pydantic model for validation.
            request_data (dict[str, Any]): Data to be validated.

        Returns:
            dict[str, Any]: Validated data as a dictionary.

        Raises:
            EhrApiError: If validation fails.
        """
        try:
            validated_data = dto_type(**request_data)
            return validated_data.model_dump(by_alias=True)
        except ValidationError as err:
            self.logger.exception("Validation failed during DTO parsing.")
            raise EhrApiError("Patient data validation error.", 400) from err

    async def __transform_filter_keys(self, filters: dict[str, Any]) -> dict[str, Any]:
        """
        Transforms filter keys to match the expected API format.

        Args:
            filters (dict[str, Any]): Input filters.

        Returns:
            dict[str, Any]: Transformed filters.
        """
        key_mapping = {
            "first_name": "name",
            "last_name": "family",
            "email": "email",
            "state": "address-state",
            "count": "_count",
            "id_number": "identifier",
            "phone": "phone",
            "gender": "gender",
            "birth_date": "birthDate",
            "organization": "organization",
            "from_date": "from_date",
            "to_date": "to_date",
            "page_size": "page_size",
        }

        return {
            key_mapping.get(key.lower(), key): value for key, value in filters.items()
        }

    async def get_all(self, next_page: Optional[str] = None) -> GetPatientResponse:
        """
        Retrieves all patients with optional pagination.

        Args:
            next_page (Optional[str]): Pagination token.

        Returns:
            GetPatientResponse: Patient data response.
        """
        try:
            params = {"nextPage": next_page} if next_page else None
            response = await self.get(
                PatientEndpoints.GET_ALL_PATIENTS,
                response_model=GetPatientResponse,
                query_params=params,
            )
            return response
        except EhrApiError as e:
            self.logger.error("Error fetching all patients: %s", e, exc_info=True)
            raise
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while fetching all patients: %s",
                e,
                exc_info=True,
            )
            raise EhrApiError(
                f"An unexpected error occurred while fetching all patients: {e}", 500
            ) from e

    async def get_by_id(self, patient_id: str) -> GetPatientResponse:
        """
        Retrieves a patient by their ID.

        Args:
            patient_id (str): The patient's unique ID.

        Returns:
            GetPatientResponse: Patient data response.

        Raises:
            EhrApiError: If the ID is invalid or the request fails.
        """
        if patient_id is None or patient_id.strip() == "":
            raise EhrApiError("Patient ID cannot be null or empty.", 400)
        try:
            response = await self.get(
                PatientEndpoints.GET_PATIENT_BY_ID.format(patient_id=patient_id),
                response_model=GetPatientResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while fetching all patients: %s",
                e,
                exc_info=True,
            )
            raise EhrApiError(
                f"An unexpected error occurred while fetching patient by Id: {e}", 500
            ) from e

    async def exists(self, patient_id: str) -> bool:
        """
        Checks if a patient exists by ID.

        Args:
            patient_id (str): The patient's unique ID.

        Returns:
            bool: True if the patient exists, otherwise False.
        """
        if not patient_id:
            return False
        try:
            response = await self.get(
                PatientEndpoints.PATIENT_EXISTS.format(patient_id=patient_id),
                GetPatientResponse,
            )
            return response.message == "Patient Found !!!"
        except EhrApiError:
            return False

        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while fetching patient: %s",
                e,
                exc_info=True,
            )
            raise EhrApiError(
                f"An unexpected error occurred while fetching patient by Id: {e}", 500
            ) from e

    async def create(self, patient: dict[str, Any]) -> CreateUpdatePatientResponse:
        """
        Creates a new patient record.

        Args:
            patient (dict[str, Any]): Patient data.

        Returns:
            CreateUpdatePatientResponse: Response with created patient details.
        """
        if not patient:
            raise EhrApiError("Patient data cannot be null.", 400)

        validated_data = await self.__validate_data(PatientDTO, patient)
        try:
            response = await self.post(
                PatientEndpoints.CREATE_PATIENT,
                validated_data,
                response_model=CreateUpdatePatientResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while creating patient: %s",
                e,
                exc_info=True,
            )
            raise EhrApiError(
                f"An unexpected error occurred while creating patient: {e}", 500
            ) from e

    async def update(
        self, update_patient_data: dict[str, Any]
    ) -> CreateUpdatePatientResponse:
        """
        Updates an existing patient record.

        Args:
            update_patient_data (dict[str, Any]): Updated patient data.

        Returns:
            CreateUpdatePatientResponse: Response with updated patient details.
        """
        if not update_patient_data:
            raise EhrApiError("Update patient data cannot be null.", 400)

        validated_data = await self.__validate_data(
            UpdatePatientDTO, update_patient_data
        )
        try:
            response = await self.put(
                PatientEndpoints.UPDATE_PATIENT,
                validated_data,
                CreateUpdatePatientResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while updating patient: %s",
                e,
                exc_info=True,
            )
            raise EhrApiError(
                f"An unexpected error occurred while updating patient: {e}", 500
            ) from e

    async def remove(self, patient_id: str) -> None:
        """
        Deletes a patient by ID.

        Args:
            patient_id (str): The patient's unique ID.

        Raises:
            EhrApiError: If the ID is invalid or the request fails.
        """
        if not patient_id:
            raise EhrApiError("Patient ID cannot be null or empty.", 400)
        try:
            await super().delete(
                PatientEndpoints.DELETE_PATIENT.format(patient_id=patient_id),
            )
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while deleting patient: %s",
                e,
                exc_info=True,
            )
            raise EhrApiError(
                f"An unexpected error occurred while deleting patient: {e}", 500
            ) from e

    async def get_by_filters(
        self, filters: dict[str, Any], next_page: Optional[str] = None
    ) -> PatientFilterResponse:
        """
        Retrieves patients based on filter criteria.

        Args:
            filters (dict[str, Any]): Filtering criteria.
            next_page (Optional[str]): Pagination token.

        Returns:
            GetPatientResponse: Filtered patient data.
        """
        try:
            validated_filters = PatientFiltersDTO(**filters).model_dump(
                by_alias=True, exclude_none=True
            )
            transformed_filters = await self.__transform_filter_keys(validated_filters)
            params = {"filters": json.dumps(transformed_filters)}
            if next_page:
                params["nextPage"] = next_page

            response = await self.get(
                PatientEndpoints.GET_PATIENT_BY_FILTERS, PatientFilterResponse, params
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while fetching patients by filters: %s",
                e,
                exc_info=True,
            )
            raise EhrApiError(
                f"An unexpected error occurred while fetching patients by filters: {e}",
                500,
            ) from e
