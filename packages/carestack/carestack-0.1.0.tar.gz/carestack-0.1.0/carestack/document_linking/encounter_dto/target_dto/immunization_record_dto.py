import logging
from typing import Any, Optional, Union
from pydantic import BaseModel, Field, field_validator

from carestack.document_linking.encounter_dto.target_dto.document_reference_dto import (
    DocumentReference,
)
from carestack.document_linking.encounter_dto.target_dto.immunization_dto import (
    Immunization,
)
from carestack.document_linking.encounter_dto.target_dto.immunization_recommendation_dto import (
    ImmunizationRecommendation,
)

logger = logging.getLogger(__name__)


class ImmunizationRecordDTO(BaseModel):
    """Represents a record of immunizations."""

    immunizations: Optional[
        list[Union[Immunization, ImmunizationRecommendation, DocumentReference]]
    ] = Field(None)

    # @field_validator("immunizations")
    # @classmethod
    # def _validate_immunizations(
    #     cls,
    #     v: Optional[list[dict[str, Any]]],
    # ) -> Optional[
    #     list[Union[Immunization, ImmunizationRecommendation, DocumentReference]]
    # ]:
    #     """
    #     Validates and transforms the immunizations list.
    #     """
    #     if v is None:
    #         return None

    #     transformed_immunizations: list[
    #         Union[Immunization, ImmunizationRecommendation, DocumentReference]
    #     ] = []
    #     for item in v:
    #         if not isinstance(item, dict):
    #             logger.warning(
    #                 "Invalid item type encountered in immunizations list: %s. Skipping this item.",
    #                 type(item),
    #             )
    #             continue
    #         if "status" in item and item.get("status"):
    #             try:
    #                 transformed_immunizations.append(Immunization(**item))
    #             except Exception as e:
    #                 logger.error(
    #                     "Error creating Immunization object: %s. Data: %s", e, item
    #                 )
    #         elif "recommendation" in item:
    #             try:
    #                 transformed_immunizations.append(ImmunizationRecommendation(**item))
    #             except Exception as e:
    #                 logger.error(
    #                     "Error creating ImmunizationRecommendation object: %s. Data: %s",
    #                     e,
    #                     item,
    #                 )
    #         elif "data" in item:
    #             try:
    #                 transformed_immunizations.append(DocumentReference(**item))
    #             except Exception as e:
    #                 logger.error(
    #                     "Error creating DocumentReference object: %s. Data: %s",
    #                     e,
    #                     item,
    #                 )
    #         else:
    #             # Handle cases where the item doesn't match any known type
    #             logger.warning(
    #                 "Unknown immunization type encountered: %s. Skipping this item.",
    #                 item,
    #             )

    #     return transformed_immunizations
