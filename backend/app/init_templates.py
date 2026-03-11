"""
Initialize builtin templates from JSON files on startup.
Ensures all templates in the database have enriched field_config with full definitions.
"""
import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.crud.template import create, get_one
from app.schemas.template import TemplateCreate
from app.field_definitions import build_field_config_from_codes


def _load_builtin_template_json(template_filename: str) -> dict:
    """Load a builtin template JSON file from the templates/ directory at project root."""
    # Navigate from app/init_templates.py to project root
    # __file__ = app/init_templates.py
    # .parent = app/
    # .parent.parent = backend/
    # .parent.parent.parent = projectroot/
    project_root = Path(__file__).parent.parent.parent
    template_path = project_root / "templates" / template_filename
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    with open(template_path, 'r') as f:
        return json.load(f)


def _enrich_field_codes(template_data: dict) -> dict:
    """Convert field_codes to enriched field_config if needed."""
    if "field_codes" in template_data:
        # New format: convert field_codes to enriched field_config
        field_codes = template_data.pop("field_codes")
        try:
            enriched_config = build_field_config_from_codes(field_codes)
            template_data["field_config"] = enriched_config
        except ValueError as e:
            print(f"Warning: Could not enrich field codes: {e}")
    return template_data


def init_builtin_templates(db: Session):
    """Initialize builtin templates from JSON files if they don't exist in the database."""
    builtin_templates = [
        "anschreiben_gewerk_template.json",
    ]
    
    for template_filename in builtin_templates:
        try:
            # Load template from JSON file
            template_data = _load_builtin_template_json(template_filename)
            
            template_id = template_data.get("id")
            
            # Check if already exists
            existing = get_one(db, template_id)
            if existing:
                print(f"Template '{template_id}' already exists in database, skipping...")
                continue
            
            # Enrich field_codes with full definitions
            template_data = _enrich_field_codes(template_data)
            
            # Create TemplateCreate schema
            template_create = TemplateCreate(
                id=template_data["id"],
                name=template_data["name"],
                description=template_data.get("description", ""),
                field_config=template_data.get("field_config", []),
                pdf_definition=template_data.get("pdf_definition", {}),
                is_builtin=True,
            )
            
            # Store in database
            template = create(db, template_create)
            print(f"✓ Initialized builtin template '{template_id}'")
        
        except FileNotFoundError as e:
            print(f"Warning: Could not load template file: {e}")
        except Exception as e:
            print(f"Error initializing template '{template_filename}': {e}")
