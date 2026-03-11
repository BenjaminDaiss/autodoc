import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.template import TemplateListItem, TemplateResponse, TemplateCreate, FieldDefinition
from app.field_definitions import build_field_config_from_codes
import app.crud.template as crud

router = APIRouter(prefix="/api/templates", tags=["templates"])


def _to_response(template) -> dict:
    """Convert ORM template to response dict with deserialized field_config and pdf_definition.
    
    Supports both legacy (field_config list) and new (field_codes list) formats.
    Always returns enriched field_config to the frontend.
    """
    field_config_raw = crud.deserialize_field_config(template)
    
    # Enrich field_codes with definitions if using new format
    if isinstance(field_config_raw, list) and len(field_config_raw) > 0:
        first_item = field_config_raw[0]
        # Check if this looks like a field code (string) or a full definition (dict)
        if isinstance(first_item, str):
            # New format: list of field codes → enrich with definitions
            try:
                field_config = build_field_config_from_codes(field_config_raw)
            except ValueError as e:
                field_config = field_config_raw  # Fallback if code is unknown
        else:
            # Legacy format: already full definitions
            field_config = field_config_raw
    else:
        field_config = field_config_raw
    
    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "field_config": field_config,
        "pdf_definition": crud.deserialize_pdf_definition(template, resolve_images=True),
        "is_builtin": template.is_builtin,
        "created_at": template.created_at,
    }


@router.get("/", response_model=List[TemplateListItem])
def list_templates(db: Session = Depends(get_db)):
    return crud.get_all(db)


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(template_id: str, db: Session = Depends(get_db)):
    template = crud.get_one(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return _to_response(template)


@router.post("/upload", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def upload_template(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a JSON file to add a new custom template at runtime.

    Supports two formats:
    
    1. Legacy format with full field definitions:
    {
      "id": "my_template",
      "name": "My Template",
      "field_config": [
        { "code": "A_1", "label": "Firmenname", "type": "text", "required": true },
        { "code": "B_2", "label": "Datum", "type": "date", "required": true }
      ],
      "pdf_definition": { ... }
    }
    
    2. New format with field codes (references hardcoded definitions):
    {
      "id": "my_template",
      "name": "My Template",
      "field_codes": ["A_1", "B_2"],
      "pdf_definition": { ... }
    }
    
    Use {{fieldCode}} for simple replacement or {{fieldCode|filter}} for formatted values.
    Supported filters: dateDE
    """
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only .json files are accepted")

    raw = await file.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")

    # Validate required top-level keys
    for key in ("id", "name", "pdf_definition"):
        if key not in data:
            raise HTTPException(status_code=400, detail=f"Missing required field: '{key}'")
    
    # Check for either field_config or field_codes (one is required)
    has_field_config = "field_config" in data
    has_field_codes = "field_codes" in data
    
    if not (has_field_config or has_field_codes):
        raise HTTPException(
            status_code=400, 
            detail="Must provide either 'field_config' (legacy) or 'field_codes' (new format)"
        )

    if not isinstance(data["pdf_definition"], dict):
        raise HTTPException(status_code=400, detail="'pdf_definition' must be a JSON object")

    # Check for duplicate ID
    existing = crud.get_one(db, data["id"])
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"A template with id '{data['id']}' already exists",
        )

    # Process field config based on which format was provided
    if has_field_codes:
        # New format: validate field codes and store as-is (will be enriched on response)
        field_codes = data["field_codes"]
        if not isinstance(field_codes, list) or len(field_codes) == 0:
            raise HTTPException(status_code=400, detail="'field_codes' must be a non-empty list")
        
        try:
            # Validate that all codes exist in field definitions
            build_field_config_from_codes(field_codes)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Store as JSON array of strings
        field_config_to_store = field_codes
    else:
        # Legacy format: validate full field definitions
        field_config = data["field_config"]
        if not isinstance(field_config, list) or len(field_config) == 0:
            raise HTTPException(status_code=400, detail="'field_config' must be a non-empty list")
        
        try:
            fields = [FieldDefinition(**f) for f in field_config]
            field_config_to_store = fields
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid field definition: {e}")

    template_in = TemplateCreate(
        id=data["id"],
        name=data["name"],
        description=data.get("description"),
        field_config=field_config_to_store,
        pdf_definition=data["pdf_definition"],
        is_builtin=False,
    )

    template = crud.create(db, template_in)
    return _to_response(template)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(template_id: str, db: Session = Depends(get_db)):
    template = crud.get_one(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if template.is_builtin:
        raise HTTPException(status_code=403, detail="Built-in templates cannot be deleted")
    crud.delete(db, template)
