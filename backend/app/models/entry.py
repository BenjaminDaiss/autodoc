from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.database import Base


class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    template_id = Column(String(100), nullable=False)  # e.g. "anschreiben_gewerk"
    name = Column(String(255), nullable=False)          # user-given entry name
    field_values = Column(Text, nullable=False)          # JSON blob: {"A_X5hX": "...", ...}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="entries")
