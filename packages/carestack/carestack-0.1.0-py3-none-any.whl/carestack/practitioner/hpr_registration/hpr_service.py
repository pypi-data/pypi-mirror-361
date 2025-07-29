from src.practitioner.hpr_registration.hpr_dto import HprAccountResponse, NonHprAccountResponse
from pydantic import BaseModel, ValidationError
from src.practitioner.hpr_registration.hpr_dto import CheckAccountExistRequestSchema, CreateHprIdWithPreVerifiedRequestBody, CreateHprIdWithPreVerifiedResponseBody, DemographicAuthViaMobileRequestSchema, DemographicAuthViaMobileResponseSchema, GenerateAadhaarOtpRequestSchema, GenerateAadhaarOtpResponseSchema, GenerateMobileOtpRequestSchema, HpIdSuggestionRequestSchema, MobileOtpResponseSchema, VerifyAadhaarOtpRequestSchema, VerifyAadhaarOtpResponseSchema, VerifyMobileOtpRequestSchema
from src.base.base_service import BaseService
from src.base.base_types import ClientConfig
from src.base.errors import EhrApiError
import logging
from typing import Any, TypeVar

T = TypeVar('T')

class HPRService(BaseService):
    """
    ProfessionalService for handling HPR registration-related operations.

    This service provides methods for interacting with the HPR registration API,
    including Aadhaar OTP generation and verification, mobile OTP handling, etc.

    Args:
        config (ClientConfig): Configuration object containing API credentials and settings.
    """

    def __init__(self, config: ClientConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)

    async def validate_data(self, dto_type:type[BaseModel], request_data: dict[str, Any]) -> dict[str, Any]:
        """
        Validates request data using Pydantic models.

        Args:
            dto_type: Pydantic model for validation.
            request_data (Dict[str, Any]): Data to be validated.

        Returns:
            Dict[str, Any]: Validated data as a dictionary.

        Raises:
            EhrApiError: If validation fails.
        """
        try:
            validated_data = dto_type(**request_data)
            return validated_data.model_dump(by_alias=True)
        except ValidationError as err:
            self.logger.exception("Validation failed with pydantic error.")
            raise EhrApiError(f"Validation failed: {err}", 400) from err

    async def _post_and_parse(self, endpoint: str, request_data: dict[str, Any], dto_type: type[BaseModel], error_message: str, response_dto_type: type[T] = None) -> T | dict[str, Any]:
        """
        Helper function to validate data, make a POST request, and parse the response.

        Args:
            endpoint (str): The API endpoint.
            request_data (dict[str, Any]): The request data.
            dto_type (Type[BaseModel]): The Pydantic model for request validation.
            error_message (str): The error message to use if the request fails.
            response_dto_type (Type[T], optional): The Pydantic model for response parsing. Defaults to None.

        Returns:
            T | dict[str, Any]: The parsed response or the raw response if no response_dto_type is provided.

        Raises:
            EhrApiError: If validation or the API request fails.
        """
        try:
            validated_data = await self.validate_data(dto_type, request_data)
            response = await self.make_post_request(endpoint, validated_data)
            if response_dto_type:
                return response_dto_type(**response)
            return response
        except EhrApiError as e:
            raise EhrApiError(e) from e
        except ValueError as e:
            self.logger.exception("Validation error details:")
            raise EhrApiError(f"Validation failed: {error_message}", 400) from e
            
    async def generate_aadhaar_otp(self, request_data: dict[str, Any]) -> GenerateAadhaarOtpResponseSchema:
        """
        Generates Aadhaar OTP.

        Args:
            request_data (Dict[str, Any]): Request data containing aadhaar number.

        Returns:
            GenerateAadhaarOtpResponseSchema: Response with txnId and mobileNumber.

        Raises:
            EhrApiError: If the request fails or validation fails.
        """
        return await self._post_and_parse(
            "/aadhaar/generateOtp",
            request_data,
            GenerateAadhaarOtpRequestSchema,
            "Error occurred while generating Aadhaar OTP",
            GenerateAadhaarOtpResponseSchema,
        )

    async def verify_aadhaar_otp(self, request_data: dict[str, Any]) -> VerifyAadhaarOtpResponseSchema:
        """
        verifies Aadhaar OTP.

        Args:
            request_data (Dict[str, Any]): Request data containing otp and domain name,idtype,restriction,txnid.

        Returns:
            VerifyAadhaarOtpResponseSchema: Response with txnId,gender,mobileNumber,email,etc.

        Raises:
            EhrApiError: If the request fails or validation fails.
        """
        return await self._post_and_parse(
            "/aadhaar/verifyOtp",
            request_data,
            VerifyAadhaarOtpRequestSchema,
            "Error occurred while verifying Aadhaar OTP",
            VerifyAadhaarOtpResponseSchema,
        )

    async def check_account_exist(self, request_data: dict[str, Any]) -> dict[str, Any]:
        """
        checks account exist.

        Args:
            request_data (Dict[str, Any]): Request data containing txnid,preverifiedcheck.

        Returns:
            CheckAccountExistResponseSchema: Response with all details.

        Raises:
            EhrApiError: If the request fails or validation fails.
        """
        response = await self._post_and_parse(
            "/check/account-exist",
            request_data,
            CheckAccountExistRequestSchema,
            "Error occurred while checking account existence",
        )
        # First, create a dictionary copy of the response
        response_dict = response.copy()

        # Remove None values from the dictionary
        filtered_response = {k: v for k, v in response_dict.items() if v is not None}

        if response.get("hprIdNumber"):
            # If hprIdNumber is not null, it's a CheckAccountExistResponseSchemaWithHprId
            response_schema = HprAccountResponse(**filtered_response)
        else:
            # If hprIdNumber is null, it's a CheckAccountExistResponseSchemaWithoutHprId
            response_schema = NonHprAccountResponse (**filtered_response)

        return response_schema

    async def demographic_auth_via_mobile(self, request_data: dict[str, Any]) -> DemographicAuthViaMobileResponseSchema:
        """
        verifies demographic auth via mobile.

        Args:
            request_data (Dict[str, Any]): Request data containing txnid,mobile number.

        Returns:
            DemographicAuthViaMobileResponseSchema: Response with verified.

        Raises:
            EhrApiError: If the request fails or validation fails.
        """
        return await self._post_and_parse(
            "/demographic-auth/mobile",
            request_data,
            DemographicAuthViaMobileRequestSchema,
            "Error occurred while verifying demographic auth via mobile",
            DemographicAuthViaMobileResponseSchema,
        )

    async def generate_mobile_otp(self, request_data: dict[str, Any]) -> MobileOtpResponseSchema:
        """
        generates mobile OTP.

        Args:
            request_data (Dict[str, Any]): Request data containing txnid,mobile.

        Returns:
            MobileOtpResponseSchema: Response with txnid.

        Raises:
            EhrApiError: If the request fails or validation fails.
        """
        return await self._post_and_parse(
            "/generate/mobileOtp",
            request_data,
            GenerateMobileOtpRequestSchema,
            "Error occurred while generating mobile OTP",
            MobileOtpResponseSchema,
        )

    async def verify_mobile_otp(self, request_data: dict[str, Any]) -> MobileOtpResponseSchema:
        """
        verifies mobile OTP.

        Args:
            request_data (Dict[str, Any]): Request data containing txnid,otp.

        Returns:
            MobileOtpResponseSchema: Response with txnid.

        Raises:
            EhrApiError: If the request fails or validation fails.
        """
        return await self._post_and_parse(
            "/verify/mobileOtp",
            request_data,
            VerifyMobileOtpRequestSchema,
            "Error occurred while verifying mobile OTP",
            MobileOtpResponseSchema,
        )

    async def get_hpr_suggestion(self, request_data: dict[str, Any]) -> list[str]:
        """
        gets hpr suggestion.

        Args:
            request_data (Dict[str, Any]): Request data containing txnid.

        Returns:
            list[str]: Response with list of suggestions.

        Raises:
            EhrApiError: If the request fails or validation fails.
        """
        return await self._post_and_parse(
            "/hpId/suggestion",
            request_data,
            HpIdSuggestionRequestSchema,
            "Error occurred while getting hpr suggestion",
        )

    async def create_hpr_id_with_preverified(self, request_data: dict[str, Any]) -> CreateHprIdWithPreVerifiedResponseBody:
        """
        create hpr id with preverified data.

        Args:
            request_data (Dict[str, Any]): Request data containing all the details.

        Returns:
            CreateHprIdWithPreVerifiedResponseBody: Response with all the details.

        Raises:
            EhrApiError: If the request fails or validation fails.
        """
        return await self._post_and_parse(
            "/create/hprIdWithPreVerified",
            request_data,
            CreateHprIdWithPreVerifiedRequestBody,
            "Error occurred while creating hpr id with preverified data",
            CreateHprIdWithPreVerifiedResponseBody,
        )
