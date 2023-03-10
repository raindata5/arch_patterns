from adapters import (
    uow,
    repository
)
from typing import (
    List,
)
from domain import model
from service_layer import services
from domain import utils
import datetime as dt
import pytest



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
    repo_fake = repository.FakeRepository([batch_nat, batch_nat_02], [order_nat, order_nat_02])
    uow_instance = uow.unit_of_work(repo_fake) 

    best_batch = services.allocate(
        model.OrderReference(order_reference=order_nat.order_reference),
        model.Sku(sku=list_ol[0].sku),
        uow_instance
    )
    assert best_batch.reference == batch_nat.reference
    assert best_batch.available_quantity == (best_batch.quantity - list_ol[0].quantity)
    assert repo_fake.committed

def test_allocate_stock_returns_404_no_sku_found():
    batch_nat, order_nat, list_ol = sample_business_objects()
    repo = repository.FakeRepository([batch_nat], [order_nat,])
    uow_instance = uow.unit_of_work(repo) 
    list_ol[0].sku = 'fake_nat_sku'
    with pytest.raises(services.InvalidSkuReference) as ex:
        best_batch = services.allocate(
            model.OrderReference(order_reference=order_nat.order_reference),
            model.Sku(sku=list_ol[0].sku),
            uow_instance
        )
    assert batch_nat.available_quantity == 30

def test_allocate_stock_returns_no_stock():
    batch_nat, order_nat, list_ol = sample_business_objects()
    batch_nat.available_quantity -= 30
    repo = repository.FakeRepository([batch_nat], [order_nat,])
    uow_instance = uow.unit_of_work(repo)
    with pytest.raises(model.NoStock):
        best_batch = services.allocate(
            model.OrderReference(order_reference=order_nat.order_reference),
            model.Sku(sku=list_ol[0].sku),
            uow_instance
        )   
    

def test_allocate_order_to_batch_if_already_allocated_idempotent():
    batch_nat, order_nat, list_ol = sample_business_objects()
    repo = repository.FakeRepository([batch_nat], [order_nat,])
    for _ in range(2):
        best_batch = services.allocate(
        model.OrderReference(order_reference=order_nat.order_reference),
        model.Sku(sku=list_ol[0].sku),
        uow.unit_of_work(repo)
    )   

    assert best_batch.available_quantity == 20

def test_do_not_allocate_if_no_matching_sku_found():
    batch_nat, order_nat, list_ol = sample_business_objects()
    order_nat.order_lines = []
    repo = repository.FakeRepository([batch_nat], [order_nat,])
    uow_instance = uow.unit_of_work(repo)
    with pytest.raises(ValueError) as ex:
        services.allocate(
            model.OrderReference(order_reference=order_nat.order_reference),
            model.Sku(sku=list_ol[0].sku),
            uow_instance
        )

def test_add_batch():
    batch_nat, order_nat, list_ol = sample_business_objects()
    repo = repository.FakeRepository(batches=[], orders=[order_nat,])
    uow_instance = uow.unit_of_work(repo)
    batch_ref=utils.random_batchref("batch")
    inserted_batch = services.add_batch(
        sku=batch_nat.sku,
        quantity=batch_nat.quantity,
        unit_of_work=uow_instance,
        ref=batch_ref
    )
    retrieved_batch = repo.get(model.Batch, model.Batch.reference, batch_ref)
    assert retrieved_batch.reference == batch_ref
    assert inserted_batch.sku == batch_nat.sku