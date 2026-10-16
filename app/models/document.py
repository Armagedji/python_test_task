from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from app.db.base import Base


class Document(Base):
    """
    Класс документа для SQLalchemy
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    rubrics = Column(ARRAY(Text), nullable=False)
    created_date = Column(DateTime, nullable=False, index=True)
