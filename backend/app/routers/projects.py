from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json

from app.database import get_db
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
import app.crud.project as crud
import app.crud.template as template_crud

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _build_initial_form_data(db: Session) -> dict:
    """Build form data object with all fields from all templates."""
    form_data = {}
    templates = template_crud.get_all(db)
    for template in templates:
        field_config = template_crud.deserialize_field_config(template)
        for field in field_config:
            # Handle both field code strings and full field definition dicts
            if isinstance(field, str):
                # field code as string - can't initialize with defaults
                code = field
            elif isinstance(field, dict):
                code = field.get('code')
            else:
                continue
            
            if code and code not in form_data:
                # Initialize with default value or empty string
                if isinstance(field, dict):
                    default_value = field.get('defaultValue')
                    if default_value == 'today':
                        # Will be set on frontend, use today's date as placeholder
                        from datetime import datetime
                        form_data[code] = datetime.now().strftime('%Y-%m-%d')
                    elif default_value:
                        form_data[code] = default_value
                    else:
                        form_data[code] = ''
                else:
                    form_data[code] = ''
    return form_data


def _to_response(project) -> dict:
    """Convert Project ORM to response dict, deserializing form_data from JSON."""
    data = {
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'form_data': None,
        'created_at': project.created_at,
        'updated_at': project.updated_at,
    }
    if project.form_data:
        try:
            data['form_data'] = json.loads(project.form_data)
        except:
            data['form_data'] = {}
    return data


@router.get("/", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    projects = crud.get_all(db)
    return [_to_response(p) for p in projects]


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    # Initialize form_data with all template fields if not provided
    if not data.form_data:
        data.form_data = _build_initial_form_data(db)
    project = crud.create(db, data)
    return _to_response(project)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_one(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return _to_response(project)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db)):
    project = crud.get_one(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    updated = crud.update(db, project, data)
    return _to_response(updated)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_one(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    crud.delete(db, project)

