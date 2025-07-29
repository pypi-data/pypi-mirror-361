import json
import logging
from typing import Any, Optional, Type

from pydantic import BaseModel, ValidationError

from carestack.base.base_service import BaseService
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import PractitionerEndPoints
from carestack.practitioner.practitioner_dto import (
    CreatePractitionerDTO,
    CreateUpdatePractitionerResponse,
    GetPractitionerResponse,
    PractitionerFilterResponse,
    PractitionerFiltersDTO,
    UpdatePractitionerDTO,
)

logger = logging.getLogger(__name__)


class Practitioner(BaseService):
    """
    SDK-friendly Practitioner for managing practitioner-related operations.

    This class provides methods for interacting with practitioner records, including retrieval,
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
            self.logger.exception("Validation failed in PractitionerService.")
            raise EhrApiError("Validation error in PractitionerService.", 400) from err

    async def __transform_filter_keys(self, filters: dict[str, Any]) -> dict[str, Any]:
        """
        Transforms filter keys to match the expected API format and removes None values.

        Args:
            filters (dict[str, Any]): Input filters.

        Returns:
            dict[str, Any]: Transformed filters.
        """
        key_mapping = {
            "firstName": "name",
            "lastName": "family",
            "state": "address-state",
            "count": "_count",
        }

        transformed_filters = {
            key_mapping.get(key, key): (
                int(value) if key_mapping.get(key, key) == "_count" else value
            )
            for key, value in filters.items()
            if value is not None
        }

        # Validate _count separately
        if "_count" in transformed_filters:
            try:
                transformed_filters["_count"] = int(transformed_filters["_count"])
            except ValueError as e:
                raise EhrApiError(
                    status_code=400,
                    message="Invalid value for _count. It should be a numeric value.",
                ) from e

        return transformed_filters

    async def get_all(self, next_page: Optional[str] = None) -> GetPractitionerResponse:
        """
        Retrieves all practitioners with optional pagination.

        Args:
            next_page (Optional[str]): Pagination token.

        Returns:
            GetPractitionerResponse: Practitioner data response.
        """
        try:
            params = {"nextPage": next_page} if next_page else None
            response = await self.get(
                PractitionerEndPoints.GET_ALL_PRACTITIONERS,
                response_model=GetPractitionerResponse,
                query_params=params,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.exception(
                "An unexpected error occurred while fetching all practitioners"
            )
            raise EhrApiError(
                f"An unexpected error occurred while fetching all practitioners: {e}",
                500,
            ) from e

    async def get_by_id(self, practitioner_id: str) -> GetPractitionerResponse:
        """
        Retrieves a practitioner by their ID.

        Args:
            practitioner_id (str): The practitioner's unique ID.

        Returns:
            GetPractitionerResponse: Practitioner data response.

        Raises:
            EhrApiError: If the ID is invalid or the request fails.
        """
        if not practitioner_id:
            raise EhrApiError("Practitioner ID cannot be null or empty.", 400)
        try:
            response = await self.get(
                PractitionerEndPoints.GET_PRACTITIONER_BY_ID.format(
                    practitioner_id=practitioner_id
                ),
                response_model=GetPractitionerResponse,
            )
            return response
        except EhrApiError as e:
            raise e

    async def exists(self, practitioner_id: str) -> bool:
        """
        Checks if a practitioner exists by ID.

        Args:
            practitioner_id (str): The practitioner's unique ID.

        Returns:
            bool: True if the practitioner exists, otherwise False.
        """
        if not practitioner_id:
            return False
        try:
            response = await self.get(
                PractitionerEndPoints.PRACTITIONER_EXISTS.format(
                    practitioner_id=practitioner_id
                ),
                response_model=GetPractitionerResponse,
            )
            return response.message == "Practitioner Found !!!"
        except EhrApiError:
            return False

    async def create(
        self, practitioner: dict[str, Any]
    ) -> CreateUpdatePractitionerResponse:
        """
        Creates a new practitioner record.

        Args:
            practitioner (dict[str, Any]): Practitioner data.

        Returns:
            CreateUpdatePractitionerResponse: Response with created practitioner details.
        """
        if not practitioner:
            raise EhrApiError("Practitioner data cannot be null.", 400)

        validated_data = await self.__validate_data(CreatePractitionerDTO, practitioner)
        try:
            response = await self.post(
                PractitionerEndPoints.CREATE_PRACTITIONER,
                validated_data,
                response_model=CreateUpdatePractitionerResponse,
            )
            return response
        except EhrApiError as e:
            if e.status_code == 409:
                raise EhrApiError(
                    "Practitioner already exists. Consider updating the existing record instead."
                ) from e
            raise EhrApiError(
                f"""Failed to create practitioner: {
                    str(e)}"""
            ) from e

    async def update(
        self, update_practitioner_data: dict[str, Any]
    ) -> CreateUpdatePractitionerResponse:
        """
        Updates an existing practitioner record.

        Args:
            update_practitioner_data (dict[str, Any]): Updated practitioner data.

        Returns:
            CreateUpdatePractitionerResponse: Response with updated practitioner details.
        """
        if not update_practitioner_data:
            raise EhrApiError("Update practitioner data cannot be null.", 400)

        validated_data = await self.__validate_data(
            UpdatePractitionerDTO, update_practitioner_data
        )
        try:
            response = await self.put(
                PractitionerEndPoints.UPDATE_PRACTITIONER,
                validated_data,
                response_model=CreateUpdatePractitionerResponse,
            )
            return response
        except EhrApiError as e:
            raise e

    async def get_by_filters(
        self, filters: dict[str, Any], next_page: Optional[str] = None
    ) -> PractitionerFilterResponse:
        """
        Retrieves practitioners based on filter criteria.

        Args:
            filters (dict[str, Any]): Filtering criteria.
            next_page (Optional[str]): Pagination token.

        Returns:
            GetPractitionerResponse: Filtered practitioner data.
        """
        try:
            validated_filters = PractitionerFiltersDTO(**filters).model_dump(
                by_alias=True, exclude_none=True
            )

            transformed_filters = await self.__transform_filter_keys(validated_filters)

            params = {"filters": json.dumps(transformed_filters)}
            if next_page:
                params["nextPage"] = next_page

            response = await self.get(
                PractitionerEndPoints.GET_PRACTITIONER_BY_FILTERS,
                PractitionerFilterResponse,
                params,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                f"An unexpected error occurred while fetching practitioners by filters: {e}"
            )
            raise EhrApiError(
                f"An unexpected error occurred while fetching practitioners by filters: {e}",
                500,
            ) from e

    async def delete(self, practitioner_id: str) -> None:
        """
        Deletes a practitioner by ID.

        Args:
            practitioner_id (str): The practitioner's unique ID.

        Raises:
            EhrApiError: If the ID is invalid or the request fails.
        """
        try:
            await super().delete(
                PractitionerEndPoints.DELETE_PRACTITIONER.format(
                    practitioner_id=practitioner_id
                )
            )
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                f"An unexpected error occurred while deleting practitioner: {e}"
            )
            raise EhrApiError(
                f"""Failed to delete practitioner: {
                    str(e)}"""
            ) from e
