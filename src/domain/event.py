from dataclasses import dataclass, field
from typing import Dict, List, Union
import datetime as dt

@dataclass
class Event:
    pass

class OutOfStockEvent(Event):
    def __init__(self, sku) -> None:
        self.sku = sku

class BatchCreated(Event):
    sku: str
    quantity: int
    eta: Union[dt.datetime, None]
    arrived: Union[bool, None]


class AllocationRequired(Event):
    order_reference: str
    sku: str
