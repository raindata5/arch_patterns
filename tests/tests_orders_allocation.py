from typing import Tuple
from pyparsing import Or
from src.main import (
    Order,
    Batch,
    OrderLine,
    allocate_batch
)
import pytest
import datetime as dt
from datetime import timedelta
@pytest.fixture()
def sample_order_and_batch() -> Tuple[Batch, Order]:
    ex_batch = Batch(reference='TKJ-23244', sku='RED-CHAIR', quantity=30, eta=dt.datetime.now(), arrived=True)
    ex_order = Order(order_reference='TGL-23245', order_lines=[
        OrderLine("RED-CHAIR", 10),
        OrderLine("TASTELESS-LAMP",1)
    ])
    return ex_batch, ex_order

@pytest.fixture()
def in_shipment_batch():
    ex_batch_in_shipment = Batch(reference='TKJ-23244', sku='RED-CHAIR', quantity=30, eta=dt.datetime.now(), arrived=False)
    ex_batch_in_shipment_long_eta = Batch(reference='TKJ-23244', sku='RED-CHAIR', quantity=30, eta=dt.datetime.now() + timedelta(60), arrived=False)
    return ex_batch_in_shipment, ex_batch_in_shipment_long_eta

def test_allocate_order_to_batch(sample_order_and_batch:Tuple[Batch, Order]):
    ex_batch, ex_order = sample_order_and_batch
    ex_batch.allocate_stock(ex_order.search_order_line(ex_batch.sku))
    assert ex_batch.available_quantity == 20

def test_can_not_allocate_order_to_batch_if_not_available(sample_order_and_batch:Tuple[Batch, Order]):
    ex_batch, ex_order = sample_order_and_batch
    ex_order.order_lines[0].quantity = 31
    ex_batch.allocate_stock(ex_order.search_order_line(ex_batch.sku))
    assert ex_batch.available_quantity == 30

def test_allocate_order_to_batch_if_already_allocated_idempotent(sample_order_and_batch:Tuple[Batch, Order]):
    ex_batch, ex_order = sample_order_and_batch
    for _ in range(2):
        ex_batch.allocate_stock(ex_order.search_order_line(ex_batch.sku))

    assert ex_batch.available_quantity == 20
    
def test_deallocate_order_line_from_batch_if_already_allocated(sample_order_and_batch:Tuple[Batch, Order]):
    ex_batch, ex_order = sample_order_and_batch
    ex_batch.allocate_stock(ex_order.search_order_line(ex_batch.sku))
    assert ex_batch.available_quantity == 20
    order_line_red_chair = ex_order.order_lines[0]
    ex_batch.deallocate_stock(order_reference=order_line_red_chair.parent_order_reference, order_line_sku=order_line_red_chair.sku) 
    assert ex_batch.available_quantity == 30
    ex_batch._orders == []
    order_line_red_chair.parent_batch = None
    #TODO: Add more validations

def test_do_not_deallocate_order_line_if_not_already_allocated(sample_order_and_batch:Tuple[Batch, Order]):
    ex_batch, ex_order = sample_order_and_batch
    order_line_red_chair = ex_order.order_lines[0]
    ex_batch.deallocate_stock(order_reference=order_line_red_chair.parent_order_reference, order_line_sku=order_line_red_chair.sku)
    assert ex_batch.available_quantity == 30
    order_line_red_chair.parent_batch = None

def test_do_not_allocate_if_no_matching_sku_found(sample_order_and_batch:Tuple[Batch, Order]):
    ex_batch, ex_order = sample_order_and_batch
    with pytest.raises(ValueError):
        ex_batch.allocate_stock(ex_order.search_order_line(ex_batch.sku + 'platypus'))

def test_sortable_batches(sample_order_and_batch:Tuple[Batch, Order], in_shipment_batch:Tuple[Batch, Batch]):
    ex_batch, ex_order = sample_order_and_batch
    ex_batch_in_shipment, ex_batch_in_shipment_long_eta = in_shipment_batch
    sorted_batches = sorted([ex_batch_in_shipment_long_eta, ex_batch, ex_batch_in_shipment])
    sorted_batches_manual = [ex_batch, ex_batch_in_shipment, ex_batch_in_shipment_long_eta]
    assert sorted_batches == sorted_batches_manual

def test_preference_for_in_stock_batch(sample_order_and_batch:Tuple[Batch, Order], in_shipment_batch:Tuple[Batch, Batch]):
    ex_batch, ex_order = sample_order_and_batch
    ex_batch_in_shipment, ex_batch_in_shipment_long_eta = in_shipment_batch
    order_line_red_chair = ex_order.order_lines[0]
    batches = [ex_batch_in_shipment, ex_batch,]
    allocate_batch(order_line_red_chair, batches)
    assert ex_batch.available_quantity == 20
    assert ex_batch_in_shipment.available_quantity == 30

def test_preference_for_earlier_batch(sample_order_and_batch:Tuple[Batch, Order], in_shipment_batch:Tuple[Batch, Batch]):
    ex_batch, ex_order = sample_order_and_batch
    ex_batch_in_shipment, ex_batch_in_shipment_long_eta = in_shipment_batch
    order_line_red_chair = ex_order.order_lines[0]
    batches = [ex_batch_in_shipment, ex_batch_in_shipment_long_eta,]
    allocate_batch(order_line_red_chair, batches)
    assert ex_batch_in_shipment.available_quantity == 20
    assert ex_batch_in_shipment_long_eta.available_quantity == 30

def test_return_batch_object():
    raise ValueError