from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Union



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

class Batch:
    def __init__(self, reference, sku, quantity) -> None:
        self.reference = reference
        self.sku = sku
        self.quantity = quantity
        self.available_quantity = quantity
        self._orders: Union[List[OrderLine], None] = []
        self._eta: str

    def allocate_stock(self, order_line: OrderLine) -> None:
            if order_line.verify_allocation(self) and not order_line.check_allocated(self):
                #TODO: Deal with OrderLine switching to different Batch
                order_line.assign_parent_batch(self)
                self.available_quantity -= order_line.quantity
    
    def deallocate_stock(self, order_reference: str, order_line_sku: str):
        #TODO: create total_ordering or just __eq__ method
        for orderline in self._orders:
            if orderline.sku == order_line_sku and orderline.parent_order_reference == order_reference:
                self._orders.remove(orderline)
                self.available_quantity += orderline.quantity