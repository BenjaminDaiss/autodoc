from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Any, Dict, Union


class FieldDefinition(BaseModel):
    code: str
    label: str
    type: str                                    # text | number | date | select
    required: Optional[bool] = False
    placeholder: Optional[str] = None
    options: Optional[List[str]] = None          # for type=select
    min: Optional[float] = None                  # for type=number
    defaultValue: Optional[str] = None           # static default (e.g. "today")
    helpText: Optional[str] = None
    showCalculation: Optional[bool] = False
    condition: Optional[Dict[str, Any]] = None   # {"field": "M_zUo9", "equals": "Abschlagsrechnung"}
    calculated: Optional[bool] = False


class TemplateBase(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    field_config: Union[List[FieldDefinition], List[str]]  # Can be full definitions or just codes
    pdf_definition: Optional[Dict[str, Any]] = None
    is_builtin: bool = False


class TemplateCreate(TemplateBase):
    pass


class TemplateResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    field_config: List[FieldDefinition]  # Always returned as full definitions (enriched from codes if needed)
    pdf_definition: Dict[str, Any]  # Now returned with images resolved
    is_builtin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TemplateListItem(BaseModel):
    """Lightweight version for listing templates (no field_config/pdf_definition payload)."""
    id: str
    name: str
    description: Optional[str] = None
    is_builtin: bool
    created_at: datetime

    model_config = {"from_attributes": True}
