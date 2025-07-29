from typing import Optional, List, Any
from pydantic import BaseModel


class ProcessDSDto(BaseModel):
    case_type: str
    files: List[str]
    public_key: Optional[str] = None
