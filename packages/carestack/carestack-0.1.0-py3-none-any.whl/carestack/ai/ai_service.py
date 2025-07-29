import logging
from typing import Any, Type, Optional, List, Dict, TypeVar

from pydantic import BaseModel, ValidationError

from carestack.base.base_service import BaseService, GetJsonFromTextResponse
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from .ai_dto import ProcessDSDto
from .ai_utils import AiUtilities

_DTO_T = TypeVar("_DTO_T", bound=BaseModel)


class AiService(BaseService):
    """
    Service for AI-related operations, such as generating discharge summaries.
    """

    def __init__(self, config: ClientConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.utilities = AiUtilities()

    async def _validate_data(
        self, dto_type: Type[_DTO_T], request_data: Dict[str, Any]
    ) -> _DTO_T:
        """
        Validates dictionary data against a Pydantic model and returns the validated instance.
        """
        try:
            validated_instance: _DTO_T = dto_type(**request_data)
            return validated_instance
        except ValidationError as err:
            self.logger.error(
                f"Pydantic validation failed: {err.errors()}", exc_info=True
            )
            raise EhrApiError(f"Validation failed: {err.errors()}", 400) from err

    async def generate_discharge_summary(self, process_ds_data: Dict[str, Any]) -> str:
        """
        Generates a discharge summary based on the provided data.

        Args:
            process_ds_data: A dictionary containing data conforming to ProcessDSDto.
                             Expected keys: 'files' (List[Any]), 'public_key' (Optional[str]).

        Returns:
            A string representing the generated discharge summary.

        Raises:
            EhrApiError: If validation fails, the API call returns an error, or an unexpected error occurs.
        """
        self.logger.info(
            f"Starting generation of discharge summary with data: {process_ds_data}"
        )
        try:
            process_ds_dto: ProcessDSDto = await self._validate_data(
                ProcessDSDto, process_ds_data
            )

            encrypted_data = await self.utilities.encryption(process_ds_dto.files)

            payload = {
                "caseType": process_ds_dto.case_type,
                "encryptedData": encrypted_data,
            }

            api_response: GetJsonFromTextResponse = await self.post(
                "/demo/generate-discharge-summary",
                payload,
                response_model=GetJsonFromTextResponse,
            )

            return api_response.response

        except EhrApiError as e:
            self.logger.error(
                f"EHR API Error during discharge summary generation: {e.message}",
                exc_info=True,
            )
            raise
        except Exception as error:
            error_message = str(error)
            self.logger.error(
                f"Unexpected error in generate_discharge_summary: {error_message}",
                exc_info=True,
            )
            raise EhrApiError(
                f"An unexpected error occurred while generating discharge summary: {error_message}",
                500,
            ) from error
