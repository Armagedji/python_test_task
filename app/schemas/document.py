from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List


class DocumentBase(BaseModel):
    """
    Схема Pydantic для документа
    """
    text: str
    rubrics: List[str]
    created_date: datetime


class DocumentInDB(DocumentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class DocumentSearchResult(DocumentInDB):
    pass
