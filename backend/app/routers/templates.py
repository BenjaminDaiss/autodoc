import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.template import TemplateListItem, TemplateResponse, TemplateCreate, FieldDefinition
import app.crud.template as crud

router = APIRouter(prefix="/api/templates", tags=["templates"])


def _to_response(template) -> dict:
    """Convert ORM template to response dict with deserialized field_config and pdf_definition."""
    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "field_config": crud.deserialize_field_config(template),
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

    Expected JSON structure:
    {
      "id": "my_template",
      "name": "My Template",
      "description": "Optional description",
      "field_config": [
        { "code": "A_1", "label": "Firmenname", "type": "text", "required": true },
        { "code": "B_2", "label": "Datum", "type": "date", "required": true }
      ],
      "pdf_definition": {
        "pageSize": "A4",
        "content": [
          { "text": "Firma: {{A_1}}" },
          { "text": "Datum: {{B_2|dateDE}}" }
        ]
      }
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
    for key in ("id", "name", "field_config", "pdf_definition"):
        if key not in data:
            raise HTTPException(status_code=400, detail=f"Missing required field: '{key}'")

    if not isinstance(data["field_config"], list) or len(data["field_config"]) == 0:
        raise HTTPException(status_code=400, detail="'field_config' must be a non-empty list")

    if not isinstance(data["pdf_definition"], dict):
        raise HTTPException(status_code=400, detail="'pdf_definition' must be a JSON object")

    # Check for duplicate ID
    existing = crud.get_one(db, data["id"])
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"A template with id '{data['id']}' already exists",
        )

    # Validate and parse each field definition
    try:
        fields = [FieldDefinition(**f) for f in data["field_config"]]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid field definition: {e}")

    template_in = TemplateCreate(
        id=data["id"],
        name=data["name"],
        description=data.get("description"),
        field_config=fields,
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
