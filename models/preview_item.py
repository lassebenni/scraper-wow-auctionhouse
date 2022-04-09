from pydantic import BaseModel, Extra
from typing import Dict, List, Optional, Union
from datetime import datetime as dt


class Durability(BaseModel, extra=Extra.allow):  # type: ignore
    value: int
    level: Optional[Dict[str, str]] = None


class Level(BaseModel, extra=Extra.allow):  # type: ignore
    value: int
    level: Optional[Dict[str, str]] = None


class Requirements(BaseModel, extra=Extra.allow):  # type: ignore
    level: Optional[Dict[str, str]] = None


class SellPrice(BaseModel, extra=Extra.allow):  # type: ignore
    value: int
    type: Optional[Dict[str, str]]
    display_strings: Dict[str, str]


class Stats(BaseModel, extra=Extra.allow):  # type: ignore
    value: int
    type: Dict[str, str]
    display: Dict[str, Union[str, Dict]]


class Armor(BaseModel, extra=Extra.allow):  # type: ignore
    display: Dict[str, Union[str, Dict]]
    value: int


class ItemSubclass(BaseModel, extra=Extra.allow):  # type: ignore
    id: int
    key: Dict[str, str]
    name: str


class ItemClass(BaseModel, extra=Extra.allow):  # type: ignore
    id: int
    key: Dict[str, str]
    name: str


class Media(BaseModel, extra=Extra.allow):  # type: ignore
    id: int
    key: Dict[str, str]


class Item(BaseModel, extra=Extra.allow):  # type: ignore
    id: int
    key: Dict[str, str]


class PreviewItem(BaseModel, extra=Extra.allow):  # type: ignore
    armor: Optional[Armor] = None
    binding: Optional[Dict[str, str]] = None
    durability: Optional[Durability] = None
    id: Optional[int]
    inventory_type: Dict[str, str]
    is_equippable: Optional[bool]
    is_stackable: Optional[bool]
    item_class: ItemClass
    item_subclass: ItemSubclass
    item: Optional[Item] = None
    level: Optional[Level] = None
    max_count: Optional[int]
    media: Media
    name: str
    purchase_price: Optional[int]
    purchase_quantity: Optional[int]
    quality: Optional[Dict[str, str]] = None
    requirements: Optional[Requirements] = None
    sell_price: Optional[SellPrice] = None
    stats: Optional[List[Stats]]
    datetime: str = dt.now().isoformat()
