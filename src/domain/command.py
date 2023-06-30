from dataclasses import dataclass, field
from typing import Dict, List, Union, Optional
import datetime as dt

class Command:
    pass

@dataclass
class CreateBatch(Command):
    sku: str
    quantity: int
    eta: Union[dt.datetime, None] = None
    arrived: Union[bool, None]= None
    ref: Union[str, None]= None

@dataclass
class Allocate(Command):
    order_reference: str
    sku: str

@dataclass
class ChangeBatchQuantity(Command):
    batch_reference: str
    new_quantity_offset: int
    sku: str