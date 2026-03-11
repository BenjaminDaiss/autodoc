from sqlalchemy.orm import Session
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from typing import List, Optional
import json


def get_all(db: Session) -> List[Project]:
    return db.query(Project).order_by(Project.created_at.desc()).all()


def get_one(db: Session, project_id: int) -> Optional[Project]:
    return db.query(Project).filter(Project.id == project_id).first()


def create(db: Session, data: ProjectCreate) -> Project:
    project_data = data.model_dump()
    # Serialize form_data to JSON if provided
    if project_data.get('form_data'):
        project_data['form_data'] = json.dumps(project_data['form_data'])
    project = Project(**project_data)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update(db: Session, project: Project, data: ProjectUpdate) -> Project:
    update_data = data.model_dump(exclude_unset=True)
    # Serialize form_data to JSON if provided
    if 'form_data' in update_data and update_data['form_data']:
        update_data['form_data'] = json.dumps(update_data['form_data'])
    for key, value in update_data.items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


def delete(db: Session, project: Project) -> None:
    db.delete(project)
    db.commit()
