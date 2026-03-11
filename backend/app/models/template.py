from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, func
from app.database import Base


class Template(Base):
    __tablename__ = "templates"

    id = Column(String(100), primary_key=True)          # slug, e.g. "anschreiben_gewerk"
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    field_config = Column(Text, nullable=False)          # JSON array of field definitions
    pdf_definition = Column(Text, nullable=False)         # JSON pdfmake definition with {{placeholder}} syntax
    is_builtin = Column(Boolean, default=False)          # True = seeded from code, read-only
    created_at = Column(DateTime(timezone=True), server_default=func.now())
