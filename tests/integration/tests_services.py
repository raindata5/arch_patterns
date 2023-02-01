from adapters import repository as repository
from typing import (
    List,
)
from domain import model
from service_layer import services
from domain import utils
import datetime as dt
import pytest

class FakeRepository(repository.Repository):
    def __init__(self, batches: List[model.Batch], orders: List[model.Order]) -> None:
        self.batches = batches
        self.orders = orders
        self.committed = 0

    def add(self, batch:model.Batch):
        self.batches.append(batch)
    
    def get(self, class_object,class_object_column, reference) -> model.Batch:
        if class_object == model.Batch:
            queried_batch = next(batch_selected for batch_selected in self.batches if batch_selected.reference == reference)
        elif class_object == model.Order:
            queried_batch = next(batch_selected for batch_selected in self.orders if batch_selected.order_reference == reference)
        return queried_batch

    def list(self, class_object,class_object_column, filter):
        column_hash_map = {
            model.Batch.sku : "sku",
            model.Batch.reference : "reference",
        }
        col = column_hash_map.get(class_object_column)
        return [batch_selected for batch_selected in self.batches if getattr(batch_selected, col) == filter]

    def commit(self):
        self.committed = 1

def sample_business_objects():
    sku_ref_natty, sku_ref_natty_01 = utils.random_sku("NaTTY"), utils.random_sku("NaTTY_01")
    batch_ref_nat = utils.random_batchref("NaT")
    order_ref_nat = utils.random_orderid("nat_order")

    batch_nat = model.Batch(reference=batch_ref_nat, sku=sku_ref_natty, quantity=30, eta=dt.datetime.now(), arrived=False)
    order_nat = model.Order(order_reference=order_ref_nat)
    order_lines_params = [
        dict(sku=sku_ref_natty, quantity=10),
        dict(sku=sku_ref_natty_01, quantity=1)
]
    list_ol = [order_nat.attach_order_line(ol) for ol in order_lines_params]
    
    batch_nat: model.Batch
    order_nat: model.Order
    list_ol: List[model.OrderLine]
    return batch_nat, order_nat, list_ol

def test_allocate_batch():
    batch_nat, order_nat, list_ol = sample_business_objects()
    batch_nat_02, order_nat_02, list_ol_02 = sample_business_objects()
    repo = FakeRepository([batch_nat, batch_nat_02], [order_nat, order_nat_02])

    best_batch = services.allocate(
        model.OrderReference(order_reference=order_nat.order_reference),
        model.Sku(sku=list_ol[0].sku),
        repo
    )
    assert best_batch.reference == batch_nat.reference
    assert best_batch.available_quantity == (best_batch.quantity - list_ol[0].quantity)
    assert repo.committed

def test_allocate_stock_returns_404_no_sku_found():
    batch_nat, order_nat, list_ol = sample_business_objects()
    repo = FakeRepository([batch_nat], [order_nat,])
    list_ol[0].sku = 'fake_nat_sku'
    with pytest.raises(services.InvalidSkuReference) as ex:
        best_batch = services.allocate(
            model.OrderReference(order_reference=order_nat.order_reference),
            model.Sku(sku=list_ol[0].sku),
            repo
        )
    assert batch_nat.available_quantity == 30

def test_allocate_stock_returns_no_stock():
    batch_nat, order_nat, list_ol = sample_business_objects()
    batch_nat.available_quantity -= 30
    repo = FakeRepository([batch_nat], [order_nat,])
    with pytest.raises(model.NoStock):
        best_batch = services.allocate(
            model.OrderReference(order_reference=order_nat.order_reference),
            model.Sku(sku=list_ol[0].sku),
            repo
        )   
    

def test_allocate_order_to_batch_if_already_allocated_idempotent():
    batch_nat, order_nat, list_ol = sample_business_objects()
    repo = FakeRepository([batch_nat], [order_nat,])
    for _ in range(2):
        best_batch = services.allocate(
        model.OrderReference(order_reference=order_nat.order_reference),
        model.Sku(sku=list_ol[0].sku),
        repo
    )   

    assert best_batch.available_quantity == 20

def test_do_not_allocate_if_no_matching_sku_found():
    batch_nat, order_nat, list_ol = sample_business_objects()
    order_nat.order_lines = []
    repo = FakeRepository([batch_nat], [order_nat,])
    with pytest.raises(ValueError) as ex:
        services.allocate(
            model.OrderReference(order_reference=order_nat.order_reference),
            model.Sku(sku=list_ol[0].sku),
            repo
        )