from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Union
from enum import Enum, IntEnum
import datetime as dt
from functools import (
    total_ordering,
) 

class ShippingState(IntEnum):
    pass

@dataclass
class OrderLine:
    sku: str
    quantity: int
    parent_order_reference: Union[Order, None] = field(default=None)
    parent_batch: Union[Batch, None] = field(default=None)

    def assign_parent_order_reference(self, order: Order):
        self.parent_order_reference = order

    def unassign_parent_batch(self, batch: Batch):
        self.parent_batch.deallocate_stock(self)

    def assign_parent_batch(self, batch: Batch):
        if self.parent_batch:
            self.unassign_parent_batch(batch=batch)

        self.parent_batch = batch
        batch._orders.append(self)

    def verify_allocation(self, batch: Batch) -> bool:
        if batch.sku == self.sku and batch.available_quantity >= self.quantity:
            return True
        return False

    def check_allocated(self, batch: Batch):
        if not self.parent_batch:
            return False
        elif batch.reference != self.parent_batch.reference:
            return False
        return True


@dataclass
class Order:
    order_reference: str
    order_lines: Union[Sequence[OrderLine], None] = field(default_factory=list)

    def __post_init__(self):
        if self.order_lines:
            [order_line.assign_parent_order_reference(self) for order_line in self.order_lines]

    def attach_order_line(self, order_line: OrderLine):
        self.order_lines.append(order_line)
        order_line.assign_parent_order_reference(self)
    def search_order_line(self, sku: str) -> Union[OrderLine,None]:
        for order_line in self.order_lines:
            if order_line.sku == sku:
                return order_line
        # TODO: Create custom error
        raise ValueError("No order_line that matches specified SKU")

class EtaDescriptor:
    def __init__(self, name=None) -> None:
        self._name = None

    def __set_name__(self, owner, name):
        self._name = name
    
    def __get__(self, instance, owner):
        if instance is None:
            return self

        tod_clock =  instance.__dict__[self._name]
        timestamp = tod_clock.timestamp()
        return timestamp

    def __set__(self, instance, value):
        instance.__dict__[self._name] = value

@total_ordering
class Batch:
    eta = EtaDescriptor()
    def __init__(self, reference, sku, quantity, eta=dt.datetime(9999,1,1), arrived = False) -> None:
        self.reference = reference
        self.sku = sku
        self.quantity = quantity
        self.available_quantity = quantity
        self._orders: Union[List[OrderLine], None] = []
        self.eta = eta
        self._arrived: bool = arrived

    def allocate_stock(self, order_line: OrderLine) -> None:
            if order_line.verify_allocation(self) and not order_line.check_allocated(self):
                #TODO: Deal with OrderLine switching to different Batch
                order_line.assign_parent_batch(self)
                self.available_quantity -= order_line.quantity
    
    def deallocate_stock(self, order_reference: str, order_line_sku: str):
        #TODO: create total_ordering r just __eq__ method
        for orderline in self._orders:
            if orderline.sku == order_line_sku and orderline.parent_order_reference == order_reference:
                self._orders.remove(orderline)
                self.available_quantity += orderline.quantity

    @property
    def arrived(self) -> bool:
        return self._arrived

    def __eq__(self, batch_object: Batch) -> bool:
        return self.eta == batch_object.eta and self.arrived == batch_object.arrived

    def __lt__(self, batch_object: Batch) -> bool:
        return self.arrived > batch_object.arrived or (self.arrived == batch_object.arrived and self.eta < batch_object.eta)

def allocate_batch(order_line, batches: List[Batch]):
    sorted_batches = sorted(batches, reverse=False)
    best_batch = sorted_batches[0]
    best_batch.allocate_stock(order_line=order_line)