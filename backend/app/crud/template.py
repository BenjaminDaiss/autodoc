import json
from sqlalchemy.orm import Session
from app.models.template import Template
from app.schemas.template import TemplateCreate
from app.templates_data import get_image_uri
from typing import List, Optional


# ─── CRUD functions ────────────────────────────────────────────────────────────

def get_all(db: Session) -> List[Template]:
    return db.query(Template).order_by(Template.is_builtin.desc(), Template.created_at.asc()).all()


def get_one(db: Session, template_id: str) -> Optional[Template]:
    return db.query(Template).filter(Template.id == template_id).first()


def create(db: Session, data: TemplateCreate) -> Template:
    # Convert field_config to JSON for storage
    # Handle both formats: list of field codes (strings) or list of FieldDefinition objects
    field_config_raw = data.field_config
    
    if isinstance(field_config_raw, list) and len(field_config_raw) > 0:
        first_item = field_config_raw[0]
        if isinstance(first_item, str):
            # New format: list of field codes (strings) - store as-is
            field_config_json = json.dumps(field_config_raw)
        else:
            # Legacy format: list of FieldDefinition objects - convert to dicts
            field_config_json = json.dumps([f.model_dump() for f in field_config_raw])
    else:
        field_config_json = json.dumps(field_config_raw)
    
    template = Template(
        id=data.id,
        name=data.name,
        description=data.description,
        field_config=field_config_json,
        pdf_definition=json.dumps(data.pdf_definition) if isinstance(data.pdf_definition, dict) else data.pdf_definition,
        is_builtin=data.is_builtin,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def delete(db: Session, template: Template) -> None:
    db.delete(template)
    db.commit()


def deserialize_field_config(template: Template) -> list:
    """Parse the JSON string back to a list for API responses."""
    try:
        return json.loads(template.field_config)
    except (json.JSONDecodeError, TypeError):
        return []


def deserialize_pdf_definition(template: Template, resolve_images: bool = True) -> dict:
    """Parse the PDF definition JSON. Optionally resolve image placeholders to base64 URIs."""
    try:
        pdf_def = json.loads(template.pdf_definition)
        if resolve_images:
            pdf_def = _replace_image_placeholders(pdf_def)
        return pdf_def
    except (json.JSONDecodeError, TypeError):
        return {}


def _replace_image_placeholders(obj):
    """Recursively replace image references (e.g., "headerImage") with base64 URIs."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "image" and isinstance(value, str) and value in ("headerImage", "footerImage"):
                obj[key] = get_image_uri(value)
            else:
                obj[key] = _replace_image_placeholders(value)
        return obj
    elif isinstance(obj, list):
        return [_replace_image_placeholders(item) for item in obj]
    else:
        return obj
