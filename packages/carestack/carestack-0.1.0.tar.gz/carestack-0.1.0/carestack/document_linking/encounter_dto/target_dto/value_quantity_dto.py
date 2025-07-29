from typing import Optional
from pydantic import BaseModel, Field


class ValueQuantity(BaseModel):
    """Represents a quantity with a value, unit, and code."""

    value: Optional[str] = Field(None)
    unit: Optional[str] = Field(None)
    code: Optional[str] = Field(None)
