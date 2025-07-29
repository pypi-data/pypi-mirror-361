"""Module for organization management operations.
This module provides functionalities for creating, updating, and deleting
facilities in the system.
"""

import logging
from typing import Any, Optional, Type

from pydantic import BaseModel, ValidationError

from carestack.base.base_service import BaseService
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import (
    UTILITY_API_ENDPOINTS,
    OrganizationsIdType,
    OrganizationEndPoints,
)
from carestack.document_linking.transformer.op_consultation import (
    GetJsonFromTextResponse,
)
from carestack.organization.organization_dto import (
    AddOrganizationDTO,
    GetOrganizationsResponse,
    LGDDistrictsListResponse,
    LGDDistrictsResponse,
    LGDStatesResponse,
    MasterDataResponse,
    MasterTypeResponse,
    OrganizationSubTypeRequest,
    OrganizationTypeRequest,
    OwnershipSubTypeRequest,
    SearchOrganizationDTO,
    SearchOrganizationResponse,
    SpecialitiesRequest,
    UpdateOrganizationDTO,
)


class Organization(BaseService):
    """
    SDK-friendly organization for managing organization-related operations.

    This class provides methods for interacting with organization records, including retrieval,
    creation, updating, and deletion.

    Args:
        config (ClientConfig): Configuration object containing API credentials and settings.
    """

    def __init__(self, config: ClientConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)

    async def __validate_data(
        self, dto_type: Type[BaseModel], request_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Validates request data using Pydantic models.

        Args:
            dto_type (Type[BaseModel]): Pydantic model class for validation.
            request_data (dict[str, Any]): Data to be validated.

        Returns:
            dict[str, Any]: Validated data as a dictionary.

        Raises:
            EhrApiError: If validation fails.
        """
        try:
            validated_data = dto_type(**request_data)
            return validated_data.model_dump(by_alias=True)
        except ValidationError as e:
            self.logger.error("Validation failed: %s", e.json())
            raise EhrApiError(f"Validation failed: {e}", 400) from e

    async def get_all(
        self, next_page: Optional[str] = None
    ) -> GetOrganizationsResponse:
        """
        Retrieves all facilities with optional pagination.

        Args:
            next_page (Optional[str]): Pagination token.

        Returns:
            GetFacilitiesResponse: organization data response.
        """
        try:
            params = {"nextPage": next_page} if next_page else None
            response = await self.get(
                OrganizationEndPoints.GET_ALL_ORGANIZATIONS,
                GetOrganizationsResponse,
                params,
            )
            if not isinstance(response, GetOrganizationsResponse):
                raise EhrApiError("Invalid response format", 500)
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error("Error fetching facilities: %s", str(e))
            raise EhrApiError(f"Failed to fetch facilities: {e}", 500) from e

    async def get_by_id(
        self, search_param: OrganizationsIdType, search_term: str
    ) -> GetOrganizationsResponse:
        """
        Retrieves a organization by its ID.

        Args:
            search_param (OrganizationsIdType): The type of ID (e.g., ACCOUNT_ID, organization_ID).
            search_term (str): The organization's unique ID.

        Returns:
            GetFacilitiesResponse: organization data response.

        Raises:
            EhrApiError: If the ID is invalid or the request fails.
        """
        try:
            response = await self.get(
                OrganizationEndPoints.GET_ORGANIZATION_BY_ID.format(
                    search_param=search_param.value, search_term=search_term
                ),
                GetOrganizationsResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "Error fetching organization by ID %s: %s", search_term, e
            )
            raise EhrApiError(
                f"Failed to fetch organization with ID: {search_term}", 500
            ) from e

    async def exists(self, search_param: OrganizationsIdType, search_term: str) -> bool:
        """
        Checks if a organization exists by ID.

        Args:
            search_param (OrganizationsIdType): The type of ID (e.g., ACCOUNT_ID, organization_ID).
            search_term (str): The organization's unique ID.

        Returns:
            bool: True if the organization exists, otherwise False.
        """
        try:
            response = await self.get(
                OrganizationEndPoints.ORGANIZATION_EXISTS.format(
                    search_param=search_param.value, search_term=search_term
                ),
                GetOrganizationsResponse,
            )
            return response.message == "Facility Found !!!"
        except EhrApiError as e:
            if e.status_code == 404:
                return False
            raise e
        except Exception as e:
            self.logger.error(
                "Error checking existence of organization %s: %s", search_term, e
            )
            raise EhrApiError(
                f"Error while checking organization {search_term}: {e}", 500
            ) from e

    async def create(self, organization: dict[str, Any]) -> str:
        """
        Registers a new organization.

        Args:
            organization (dict[str, Any]): organization data.

        Returns:
            str: Response message.
        """

        try:
            validated_data = await self.__validate_data(
                AddOrganizationDTO, organization
            )
            response = await self.post(
                OrganizationEndPoints.REGISTER_ORGANIZATION,
                validated_data,
                response_model=GetJsonFromTextResponse,
            )

            # if not isinstance(message, str):
            #     raise EhrApiError(
            #         "Invalid response: 'message' key is missing or not a string", 500
            #     )
            return response.response
        except EhrApiError:
            raise
        except Exception as e:
            self.logger.error("Error registering organization: %s", e)
            raise EhrApiError(f"Failed to register organization: {e}", 500) from e

    async def update(self, update_organization_data: UpdateOrganizationDTO) -> str:
        """
        Updates an existing organization record.

        Args:
            update_organization_data (dict[str, Any]): Updated organization data.

        Returns:
            str: Response message.
        """

        try:
            validated_data = await self.__validate_data(
                UpdateOrganizationDTO,
                update_organization_data.model_dump(by_alias=True),
            )
            response = await self.put(
                OrganizationEndPoints.UPDATE_ORGANIZATION,
                validated_data,
                GetJsonFromTextResponse,
            )

            return response.response
        except EhrApiError:
            raise
        except Exception as e:
            self.logger.error("Error updating organization: %s", e)
            raise EhrApiError(f"Failed to update organization: {e}", 500) from e

    async def remove(self, organization_id: str) -> str:
        """
        Deletes a organization by ID.

        Args:
            organization_id (str): The organization's unique ID.

        Returns:
            str: Response message.

        Raises:
            EhrApiError: If the ID is invalid or the request fails.
        """

        try:
            response = await self.delete(
                OrganizationEndPoints.DELETE_ORGANIZATION.format(
                    organization_id=organization_id
                )
            )
            if not isinstance(response, dict):
                return "service not available"
            message = response and response.get("message", "")
            return message

        except EhrApiError:
            raise
        except Exception as e:
            self.logger.error("Error deleting organization %s: %s", organization_id, e)
            raise EhrApiError(
                f"Failed to delete organization {organization_id}: {e}", 500
            ) from e

    async def search_organization(
        self, search_organization_data: SearchOrganizationDTO
    ) -> SearchOrganizationResponse:
        """
        Searches for a organization.

        Args:
            search_organization_data: The search criteria.

        Returns:
            A SearchorganizationResponse object containing the search results.

        Raises:
            EhrApiError: If there is an error during the API request.
        """
        try:
            validated_data = await self.__validate_data(
                SearchOrganizationDTO,
                search_organization_data.model_dump(by_alias=True),
            )
            response = await self.post(
                OrganizationEndPoints.SEARCH_ORGANIZATION,
                validated_data,
                SearchOrganizationResponse,
            )
            return response
        except EhrApiError as e:
            self.logger.error(f"Error while searching for organization: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while searching for organization: {e}")
            raise EhrApiError(
                f"Unexpected error while searching for organization: {e}", 500
            ) from e

    async def get_master_types(self) -> MasterTypeResponse:
        """
        Retrieves master types from the external API.
        """
        try:
            response = await self.get(
                UTILITY_API_ENDPOINTS.MASTER_TYPES, MasterTypeResponse
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error("Error getting master types: %s", e)
            raise EhrApiError(f"Failed to get master types: {e}", 500) from e

    async def get_master_data(self, data_type: str) -> MasterDataResponse:
        """
        Retrieves master data of a specific type from the external API.
        """
        try:
            response = await self.get(
                UTILITY_API_ENDPOINTS.MASTER_DATA_BY_TYPE.format(type=data_type),
                MasterDataResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(f"Error getting master data of type {data_type}: {e}")
            raise EhrApiError(
                f"Failed to get master data of type {data_type}: {e}", 500
            ) from e

    async def get_lgd_states(self) -> LGDStatesResponse:
        """
        Retrieves LGD states from the external API.
        """
        try:
            response = await self.get(
                UTILITY_API_ENDPOINTS.STATES_AND_DISTRICTS, LGDStatesResponse
            )
            if not isinstance(response, LGDStatesResponse):
                raise EhrApiError(
                    "Invalid response format from LGD states API: Expected a list.", 500
                )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error("Error getting LGD states: %s", e)
            raise EhrApiError(f"Failed to get LGD states: {e}", 500) from e

    async def get_lgd_sub_districts(
        self, district_code: str
    ) -> LGDDistrictsListResponse:
        """
        Retrieves LGD sub-districts for a given district code from the external API.
        """
        try:
            response = await self.get(
                UTILITY_API_ENDPOINTS.SUBDISTRICTS.format(district_code=district_code),
                LGDDistrictsListResponse,
            )
            if not isinstance(response, LGDDistrictsListResponse):
                raise EhrApiError(
                    "Invalid response format from LGD states API: Expected a list.", 500
                )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "Error getting LGD sub-districts for district code %s: %s",
                district_code,
                e,
            )
            raise EhrApiError(
                f"Failed to get LGD sub-districts for district code {district_code}: {e}",
                500,
            ) from e

    async def get_organization_type(
        self, request_body: OrganizationTypeRequest
    ) -> MasterDataResponse:
        """
        Retrieves organization types based on the request body from the external API.

        Args:
            request_body (organizationTypeRequest): The request body containing ownershipCode and optional systemOfMedicineCode.

        Returns:
            dict[str, Any]: The response from the external API.

        Raises:
            EhrApiError: If there is an error during the API request or validation.
        """
        try:
            validated_data = await self.__validate_data(
                OrganizationTypeRequest, request_body.model_dump(by_alias=True)
            )
            response = await self.post(
                UTILITY_API_ENDPOINTS.ORGANIZATION_TYPE,
                validated_data,
                MasterDataResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error("Error getting organization types: %s", e)
            raise EhrApiError(f"Failed to get organization types: {e}", 500) from e

    async def get_owner_subtypes(
        self, request_body: OwnershipSubTypeRequest
    ) -> MasterDataResponse:
        """
        Retrieves owner subtypes based on the request body from the external API.

        Args:
            request_body (OwnershipSubTypeRequest): The request body containing ownershipCode and optional ownerSubtypeCode.

        Returns:
            dict[str, Any]: The response from the external API.

        Raises:
            EhrApiError: If there is an error during the API request or validation.
        """
        try:
            validated_data = await self.__validate_data(
                OwnershipSubTypeRequest, request_body.model_dump(by_alias=True)
            )
            response = await self.post(
                UTILITY_API_ENDPOINTS.OWNER_SUBTYPE, validated_data, MasterDataResponse
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error("Error getting owner subtypes: %s", e)
            raise EhrApiError(f"Failed to get owner subtypes: {e}", 500) from e

    async def get_specialities(
        self, request_body: SpecialitiesRequest
    ) -> MasterDataResponse:
        """
        Retrieves specialities based on the request body from the external API.

        Args:
            request_body (SpecialitiesRequest): The request body containing systemOfMedicineCode.

        Returns:
            dict[str, Any]: The response from the external API.

        Raises:
            EhrApiError: If there is an error during the API request or validation.
        """
        try:
            validated_data = await self.__validate_data(
                SpecialitiesRequest, request_body.model_dump(by_alias=True)
            )
            response = await self.post(
                UTILITY_API_ENDPOINTS.SPECIALITIES, validated_data, MasterDataResponse
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error("Error getting specialities: %s", e)
            raise EhrApiError(f"Failed to get specialities: {e}", 500) from e

    async def get_organization_subtypes(
        self, request_body: OrganizationSubTypeRequest
    ) -> MasterDataResponse:
        """
        Retrieves organization subtypes based on the request body from the external API.

        Args:
            request_body (organizationSubTypeRequest): The request body containing organizationTypeCode.

        Returns:
            dict[str, Any]: The response from the external API.

        Raises:
            EhrApiError: If there is an error during the API request or validation.
        """
        try:
            validated_data = await self.__validate_data(
                OrganizationSubTypeRequest, request_body.model_dump(by_alias=True)
            )
            response = await self.post(
                UTILITY_API_ENDPOINTS.ORGANIZATION_SUBTYPE,
                validated_data,
                MasterDataResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error("Error getting organization subtypes: %s", e)
            raise EhrApiError(f"Failed to get organization subtypes: {e}", 500) from e
