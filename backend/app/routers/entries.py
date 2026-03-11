import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.entry import EntryCreate, EntryUpdate, EntryResponse
import app.crud.entry as crud
import app.crud.project as project_crud

router = APIRouter(prefix="/api/projects/{project_id}/entries", tags=["entries"])


def _to_response(entry) -> dict:
    """Convert ORM entry to response dict, deserializing the JSON field_values."""
    return {
        "id": entry.id,
        "project_id": entry.project_id,
        "template_id": entry.template_id,
        "name": entry.name,
        "field_values": crud.deserialize_field_values(entry),
        "created_at": entry.created_at,
        "updated_at": entry.updated_at,
    }


def _require_project(project_id: int, db: Session):
    project = project_crud.get_one(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/", response_model=List[EntryResponse])
def list_entries(project_id: int, db: Session = Depends(get_db)):
    _require_project(project_id, db)
    entries = crud.get_all(db, project_id)
    return [_to_response(e) for e in entries]


@router.post("/", response_model=EntryResponse, status_code=status.HTTP_201_CREATED)
def create_entry(project_id: int, data: EntryCreate, db: Session = Depends(get_db)):
    _require_project(project_id, db)
    entry = crud.create(db, project_id, data)
    return _to_response(entry)


@router.get("/{entry_id}", response_model=EntryResponse)
def get_entry(project_id: int, entry_id: int, db: Session = Depends(get_db)):
    _require_project(project_id, db)
    entry = crud.get_one(db, project_id, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return _to_response(entry)


@router.put("/{entry_id}", response_model=EntryResponse)
def update_entry(project_id: int, entry_id: int, data: EntryUpdate, db: Session = Depends(get_db)):
    _require_project(project_id, db)
    entry = crud.get_one(db, project_id, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    entry = crud.update(db, entry, data)
    return _to_response(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(project_id: int, entry_id: int, db: Session = Depends(get_db)):
    _require_project(project_id, db)
    entry = crud.get_one(db, project_id, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    crud.delete(db, entry)
