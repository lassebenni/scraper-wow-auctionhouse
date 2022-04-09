from pydantic import BaseModel, Extra
from typing import List, Optional, TypedDict
from datetime import datetime as dt
import uuid


class LotItemModifier(TypedDict):
    type: int
    value: int


class LotItem(BaseModel, extra=Extra.allow):  # type: ignore
    id: int
    modifiers: Optional[List[LotItemModifier]] = None


class Lot(BaseModel, extra=Extra.allow):  # type: ignore
    id: int
    item: LotItem
    buyout: Optional[int] = 0
    quantity: int
    time_left: str
    unit_price: Optional[int] = -1
    bid: Optional[int] = None
    ingestion_datetime: str = dt.now().isoformat()
    ingestion_date: str = dt.now().date().isoformat()


class Lots(BaseModel):
    lots: List[Lot]


def create_unique_id():
    return str(uuid.uuid4())
