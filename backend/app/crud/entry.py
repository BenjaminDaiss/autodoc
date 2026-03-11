import json
from sqlalchemy.orm import Session
from app.models.entry import Entry
from app.schemas.entry import EntryCreate, EntryUpdate
from typing import List, Optional


def get_all(db: Session, project_id: int) -> List[Entry]:
    return (
        db.query(Entry)
        .filter(Entry.project_id == project_id)
        .order_by(Entry.created_at.desc())
        .all()
    )


def get_one(db: Session, project_id: int, entry_id: int) -> Optional[Entry]:
    return (
        db.query(Entry)
        .filter(Entry.project_id == project_id, Entry.id == entry_id)
        .first()
    )


def create(db: Session, project_id: int, data: EntryCreate) -> Entry:
    entry = Entry(
        project_id=project_id,
        template_id=data.template_id,
        name=data.name,
        field_values=json.dumps(data.field_values),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def update(db: Session, entry: Entry, data: EntryUpdate) -> Entry:
    if data.name is not None:
        entry.name = data.name
    if data.field_values is not None:
        entry.field_values = json.dumps(data.field_values)
    db.commit()
    db.refresh(entry)
    return entry


def delete(db: Session, entry: Entry) -> None:
    db.delete(entry)
    db.commit()


def deserialize_field_values(entry: Entry) -> dict:
    """Parse the JSON string back to a dict for API responses."""
    try:
        return json.loads(entry.field_values)
    except (json.JSONDecodeError, TypeError):
        return {}
