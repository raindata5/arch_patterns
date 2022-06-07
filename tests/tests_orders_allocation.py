from typing import Tuple
from pyparsing import Or
from src.main import (
    Order,
    Batch,
    OrderLine
)
import pytest

@pytest.fixture()
def sample_order_and_batch() -> Tuple[Batch, Order]:
    OrderLine
    ex_batch = Batch(reference='TKJ-23244', sku='RED-CHAIR', quantity=30)
    ex_order = Order(order_reference='TGL-23245', order_lines=[
        OrderLine("RED-CHAIR", 10),
        OrderLine("TASTELESS-LAMP",1)
    ])
    return ex_batch, ex_order

def test_allocate_order_to_batch(sample_order_and_batch:Tuple[Batch, Order]):
    ex_batch, ex_order = sample_order_and_batch
    ex_batch.allocate_stock(ex_order)
    assert ex_batch.available_quantity == 20

def test_can_not_allocate_order_to_batch_if_not_available(sample_order_and_batch:Tuple[Batch, Order]):
    ex_batch, ex_order = sample_order_and_batch
    ex_order.order_lines[0].quantity = 31
    ex_batch.allocate_stock(ex_order)
    assert ex_batch.available_quantity == 30

def test_allocate_order_to_batch_if_already_allocated(sample_order_and_batch:Tuple[Batch, Order]):
    ex_batch, ex_order = sample_order_and_batch
    for _ in range(2):
        ex_batch.allocate_stock(ex_order)

    assert ex_batch.available_quantity == 20
    
def test_deallocate_order_line_from_batch_if_already_allocated(sample_order_and_batch:Tuple[Batch, Order]):
    ex_batch, ex_order = sample_order_and_batch
    ex_batch.allocate_stock(ex_order)
    assert ex_batch.available_quantity == 20
    order_line_red_chair = ex_order.order_lines[0]
    ex_batch.deallocate_stock(order_reference=order_line_red_chair.parent_order_reference, order_line_sku=order_line_red_chair.sku) 
    assert ex_batch.available_quantity == 30
    #TODO: Add more validations