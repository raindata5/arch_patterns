from domain.model import (
    Order,
    Batch,
    OrderLine,
    NoStock
)
from domain.utils import (
    allocate_batch,
)
from typing import Tuple
import pytest
import datetime as dt
from datetime import timedelta

@pytest.fixture()
def sample_order_and_batch() -> Tuple[Batch, Order]:
    ex_batch = Batch(reference='TKJ-23244', sku='RED-CHAIR', quantity=30, eta=dt.datetime.now(), arrived=True)
    ex_order = Order(order_reference='TGL-23245')

    order_lines_params = [
        dict(sku="RED-CHAIR", quantity=10),
        dict(sku="TASTELESS-LAMP", quantity=1)
    ]
    [ex_order.attach_order_line(ol) for ol in order_lines_params]
    return ex_batch, ex_order

@pytest.fixture()
def in_shipment_batch():
    ex_batch_in_shipment = Batch(reference='TKJ-23244', sku='RED-CHAIR', quantity=30, eta=dt.datetime.now(), arrived=False)
    ex_batch_arrived_long_eta = Batch(reference='TKJ-23244', sku='RED-CHAIR', quantity=30, eta=dt.datetime.now() + timedelta(60), arrived=True)
    return ex_batch_in_shipment, ex_batch_arrived_long_eta
    
def test_deallocate_order_line_from_batch_if_already_allocated(sample_order_and_batch:Tuple[Batch, Order]):
    ex_batch, ex_order = sample_order_and_batch
    ex_batch.allocate_stock(ex_order)
    assert ex_batch.available_quantity == 20
    order_line_red_chair = next(ol for ol in ex_order.order_lines if ol.sku == "RED-CHAIR")
    ex_batch.deallocate_stock(order_reference=order_line_red_chair.parent_order_reference, order_line_sku=order_line_red_chair.sku) 
    assert ex_batch.available_quantity == 30
    ex_batch.orders == []
    #TODO: Add more validations

def test_do_not_deallocate_order_line_if_not_already_allocated(sample_order_and_batch:Tuple[Batch, Order]):
    ex_batch, ex_order = sample_order_and_batch
    order_line_red_chair = next(ol for ol in ex_order.order_lines if ol.sku == "RED-CHAIR")
    ex_batch.deallocate_stock(order_reference=order_line_red_chair.parent_order_reference, order_line_sku=order_line_red_chair.sku)
    assert ex_batch.available_quantity == 30

def test_sortable_batches(sample_order_and_batch:Tuple[Batch, Order], in_shipment_batch:Tuple[Batch, Batch]):
    ex_batch, ex_order = sample_order_and_batch
    ex_batch_in_shipment, ex_batch_arrived_long_eta = in_shipment_batch
    sorted_batches = sorted([ex_batch_arrived_long_eta, ex_batch, ex_batch_in_shipment])
    sorted_batches_manual = [ex_batch, ex_batch_arrived_long_eta, ex_batch_in_shipment]
    assert sorted_batches == sorted_batches_manual

def test_preference_for_in_stock_batch(sample_order_and_batch:Tuple[Batch, Order], in_shipment_batch:Tuple[Batch, Batch]):
    ex_batch, ex_order = sample_order_and_batch
    ex_batch_in_shipment, ex_batch_arrived_long_eta = in_shipment_batch
    order_line_red_chair = next(ol for ol in ex_order.order_lines if ol.sku == "RED-CHAIR")
    batches = [ex_batch_in_shipment, ex_batch, ex_batch_arrived_long_eta]
    allocate_batch(ex_order, batches)
    assert ex_batch.available_quantity == 20
    assert ex_batch_in_shipment.available_quantity == 30

def test_preference_for_earlier_batch(sample_order_and_batch:Tuple[Batch, Order], in_shipment_batch:Tuple[Batch, Batch]):
    ex_batch, ex_order = sample_order_and_batch
    ex_batch_in_shipment, ex_batch_arrived_long_eta = in_shipment_batch
    order_line_red_chair = next(ol for ol in ex_order.order_lines if ol.sku == "RED-CHAIR")
    batches = [ex_batch_in_shipment, ex_batch_arrived_long_eta,]
    batch_allocation = allocate_batch(ex_order, batches)
    assert ex_batch_in_shipment.available_quantity == 30
    assert ex_batch_arrived_long_eta.available_quantity == 20
    assert batch_allocation.reference == ex_batch_arrived_long_eta.reference

# def test_return_batch_object():
#     raise ValueError