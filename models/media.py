from pydantic import BaseModel, Extra
from typing import List
from datetime import datetime as dt
import uuid


class Assets(BaseModel, extra=Extra.allow):  # type: ignore
    key: str
    value: str
    file_data_id: int


class Media(BaseModel, extra=Extra.allow):  # type: ignore
    id: int
    assets: List[Assets]
    ingestion_datetime: str = dt.now().isoformat()
    ingestion_date: str = dt.now().date().isoformat()


class Medias(BaseModel):
    media: List[Media]


def create_unique_id():
    return str(uuid.uuid4())
