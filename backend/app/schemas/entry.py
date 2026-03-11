from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class EntryBase(BaseModel):
    name: str
    template_id: str
    field_values: Dict[str, Any]


class EntryCreate(EntryBase):
    pass


class EntryUpdate(BaseModel):
    name: Optional[str] = None
    field_values: Optional[Dict[str, Any]] = None


class EntryResponse(EntryBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
