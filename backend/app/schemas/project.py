from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    form_data: Optional[Dict[str, Any]] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    form_data: Optional[Dict[str, Any]] = None


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
