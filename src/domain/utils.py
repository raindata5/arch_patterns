from __future__ import annotations
import logging
from types import MethodType
from typing import List
from functools import (
    partial,
    wraps
)
import uuid
from domain import event
class CheckOrderLineMatch:
    """
    This callable object determines whether an orderline
    is identical to another and can be used as a standalone
    function or as a method on a class through the descriptor protocol.
    """
    def __init__(self, name=None):
        self._name = None

    def __set_name__(self, owner, name):
        self._name = name

    def __call__(self, instance, order_reference: str, order_line_sku: str) -> bool:
        if instance.sku == order_line_sku and instance.parent_order_reference == order_reference:
            return True
        return False

    def __get__(self, instance, owner):
        return MethodType(self, instance)


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

eta_descriptor = partial(EtaDescriptor, "eta")
from domain import model
def allocate_batch(order, batches: List) -> model.Batch:
    # find a way to iterate through batches
    sorted_batches = sorted(batches, reverse=False)
    # for b in sorted_batches:
    #     if best_batch.allocate_stock(order) := best_batch_result
    try:
        best_batch_result = next(b for b in sorted_batches if b.allocate_stock(order))
    except StopIteration as ex:
        logging.info(ex)
        return None
    return best_batch_result


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name=""):
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name=""):
    return f"order-{name}-{random_suffix()}"

def object_sensor(callable,):

    @wraps(callable)
    def wrapped_function(*args, **kwargs):
        result = callable(*args, **kwargs)
        if result:
            self = args[0]
            self.seen.append(result)
        return result
    
    return wrapped_function

def out_of_stock_handler(event: event.OutOfStockEvent):
    logging.info(f'Creating a PO for {event.sku}')