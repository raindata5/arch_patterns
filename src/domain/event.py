from dataclasses import dataclass, field
from typing import Dict, List, Union, Optional
import datetime as dt


class Event:
    pass

class OutOfStockEvent(Event):
    def __init__(self, sku) -> None:
        self.sku = sku

@dataclass
class BatchCreated(Event):
    sku: str
    quantity: int
    eta: Union[dt.datetime, None] = None
    arrived: Union[bool, None]= None
    ref: Union[str, None]= None

@dataclass
class AllocationRequired(Event):
    order_reference: str
    sku: str

@dataclass
class BatchQuantityChanged(Event):
    batch_reference: str
    new_quantity_offset: int
    sku: str