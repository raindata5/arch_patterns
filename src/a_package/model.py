from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Union
import datetime as dt
from functools import (
    total_ordering
)
from a_package import utils
from a_package import model

@dataclass(unsafe_hash=True)
class OrderLine:
    check_order_line_match = utils.CheckOrderLineMatch()
    sku: str
    quantity: int
    parent_order_reference: str

    def verify_allocation(self, batch: Batch) -> bool:
        if batch.sku == self.sku and batch.available_quantity >= self.quantity:
            return True
        elif batch.available_quantity < self.quantity:
            raise NoStock()
        return False

    def check_allocation_status(self, batch: Batch):
        for batch_ol in batch._orders:
            if batch_ol == self:
                return True
        return False


@dataclass
class Order:
    order_reference: str
    order_lines: list = field(default_factory=list)

    def __post_init__(self):
        if self.order_lines:
            print(self.__repr__())

    def attach_order_line(self, order_line_params:Dict):
        ol = OrderLine(**order_line_params, parent_order_reference=self.order_reference)
        self.order_lines.append(ol)
        return ol

    def remove_order_line(self, order_line):
        if order_line in self.order_lines:
            self.order_lines.remove(order_line)
            return order_line

    def search_order_line(self, sku: str) -> Union[OrderLine,None]:
        for order_line in self.order_lines:
            if order_line.sku == sku:
                return order_line
        # TODO: Create custom error
        raise ValueError("No order_line that matches specified SKU")


@total_ordering
class Batch:
    eta = utils.eta_descriptor()
    # eta = EtaDescriptor() # Tradeoffs between the two?
    
    def __init__(self, reference, sku, quantity, eta=dt.datetime(9999,1,1), arrived = False) -> None:
        self.reference = reference
        self.sku = sku
        self.quantity = quantity
        self.available_quantity = quantity
        self._orders: List[OrderLine]= []
        self.eta = eta
        self.arrived: bool = arrived

    def allocate_stock(self, order_line: OrderLine) -> None:
            if order_line.verify_allocation(self) and not order_line.check_allocation_status(self):
                #TODO: Deal with OrderLine switching to different Batch
                self._orders.append(order_line)
                self.available_quantity -= order_line.quantity
    
    def deallocate_stock(self, order_reference: str, order_line_sku: str):
        #TODO: create total_ordering r just __eq__ method
        # create order_line_match method as a descriptor
        # add generator
        for orderline in self._orders:
            if orderline.check_order_line_match(order_reference, order_line_sku):
                self._orders.remove(orderline)
                self.available_quantity += orderline.quantity

    def __eq__(self, batch_object: Batch) -> bool:
        # return self.eta == batch_object.eta and self.arrived == batch_object.arrived
        return self.reference == batch_object.reference

    def __lt__(self, batch_object: Batch) -> bool:
        return self.arrived > batch_object.arrived or (self.arrived == batch_object.arrived and self.eta < batch_object.eta)

    def __repr__(self) -> str:
        return f"Batch(reference={self.reference!r},)"

class NoStock(Exception):
    """An exception expressing that there was an attempt to 
    assign an orderline to a batch with insufficient stock """