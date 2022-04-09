from pydantic import BaseModel, Extra
from typing import Dict, List
from datetime import datetime as dt
import uuid

from models.preview_item import PreviewItem


class ItemSubclass(BaseModel, extra=Extra.allow):  # type: ignore
    id: int
    key: Dict[str, str]
    name: str


class ItemClass(BaseModel, extra=Extra.allow):  # type: ignore
    id: int
    key: Dict[str, str]
    name: str


class ItemMedia(BaseModel, extra=Extra.allow):  # type: ignore
    id: int
    key: Dict[str, str]


class Item(BaseModel, extra=Extra.allow):  # type: ignore
    id: int
    name: str
    quality: Dict[str, str]
    level: int
    media: ItemMedia
    item_class: ItemClass
    item_subclass: ItemSubclass
    inventory_type: Dict[str, str]
    purchase_price: int
    sell_price: int
    max_count: int
    is_equippable: bool
    is_stackable: bool
    preview_item: PreviewItem
    purchase_quantity: int
    ingestion_datetime: str = dt.now().isoformat()
    ingestion_date: str = dt.now().date().isoformat()


class Items(BaseModel):
    items: List[Item]


def create_unique_id():
    return str(uuid.uuid4())
