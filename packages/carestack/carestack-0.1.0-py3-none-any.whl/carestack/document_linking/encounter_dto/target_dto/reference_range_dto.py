from pydantic import BaseModel, Field, field_validator

from carestack.document_linking.encounter_dto.target_dto.value_quantity_dto import (
    ValueQuantity,
)


class ReferenceRange(BaseModel):
    """Represents a reference range for a value, including low and high quantities."""

    low: ValueQuantity = Field(...)
    high: ValueQuantity = Field(...)

    # @field_validator("high")
    # @classmethod
    # def validate_range(cls, high_val, values):
    #     """Validate that high value is greater than or equal to low value."""
    #     low_val = values.get("low")
    #     if (
    #         low_val
    #         and high_val
    #         and low_val.value is not None
    #         and high_val.value is not None
    #     ):
    #         try:
    #             if float(low_val.value) > float(high_val.value):
    #                 raise ValueError(
    #                     "Low value must be less than or equal to high value"
    #                 )
    #         except ValueError:
    #             # If values can't be converted to float, skip validation
    #             pass
    #     return high_val
