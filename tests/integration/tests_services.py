from adapters import (
    uow,
    repository
)
from typing import (
    List,
)
from domain import (
    model,
    event
)
from service_layer import services, message_bus
from domain import utils
import datetime as dt
import pytest


def sample_business_objects():
    sku_ref_natty, sku_ref_natty_01 = utils.random_sku("NaTTY"), utils.random_sku("NaTTY_01")
    batch_ref_nat = utils.random_batchref("NaT")
    order_ref_nat = utils.random_orderid("nat_order")

    batch_nat = model.Batch(reference=batch_ref_nat, sku=sku_ref_natty, quantity=30, eta=dt.datetime.now(), arrived=False)
    product_nat = model.Product(sku=sku_ref_natty, batches=[batch_nat])
    order_nat = model.Order(order_reference=order_ref_nat)
    order_lines_params = [
        dict(sku=sku_ref_natty, quantity=10),
        dict(sku=sku_ref_natty_01, quantity=1)
]
    list_ol = [order_nat.attach_order_line(ol) for ol in order_lines_params]
    
    batch_nat: model.Batch
    order_nat: model.Order
    list_ol: List[model.OrderLine]
    return product_nat, order_nat, list_ol

def test_allocate_batch():
    product_nat, order_nat, list_ol = sample_business_objects()
    product_nat_02, order_nat_02, list_ol_02 = sample_business_objects()
    repo_fake = repository.FakeRepository([product_nat, product_nat_02], [order_nat, order_nat_02])
    uow_instance = uow.unit_of_work(repo_fake) 
    event_new = event.AllocationRequired(
        order_reference=order_nat.order_reference,
        sku=list_ol[0].sku
    )

    best_batch = services.allocate(
        event_new,
        uow_instance
    )
    assert best_batch.reference == product_nat.batches[0].reference
    assert best_batch.available_quantity == (best_batch.quantity - list_ol[0].quantity)
    assert repo_fake.committed

def test_allocate_stock_returns_404_no_sku_found():
    product_nat, order_nat, list_ol = sample_business_objects()
    repo = repository.FakeRepository([product_nat], [order_nat,])
    uow_instance = uow.unit_of_work(repo) 
    list_ol[0].sku = 'fake_nat_sku'
    event_new = event.AllocationRequired(
        order_reference=order_nat.order_reference,
        sku=list_ol[0].sku
    )
    with pytest.raises(services.InvalidSkuReference) as ex:
        results = services.allocate(
            event_new,
            uow_instance
        )
    assert product_nat.batches[0].available_quantity == 30

def test_allocate_stock_returns_no_stock():
    product_nat, order_nat, list_ol = sample_business_objects()
    product_nat.batches[0].available_quantity -= 30
    repo = repository.FakeRepository([product_nat], [order_nat,])
    uow_instance = uow.unit_of_work(repo)
    # with pytest.raises(model.NoStock):
    event_new = event.AllocationRequired(
        order_reference=order_nat.order_reference,
        sku=list_ol[0].sku
    )
    results = services.allocate(
        event_new,
        uow_instance
    )   
    inserted_batch=results[0]
    event_ret = list(repo.collect_new_events())[0]
    assert type(event_ret) == event.OutOfStockEvent 
    

def test_allocate_order_to_batch_if_already_allocated_idempotent():
    product_nat, order_nat, list_ol = sample_business_objects()
    repo = repository.FakeRepository([product_nat], [order_nat,])
    for _ in range(2):
        best_batch = services.allocate(
            event.AllocationRequired(
                order_reference=order_nat.order_reference,
                sku=list_ol[0].sku
            ),
        uow.unit_of_work(repo)
    )   

    assert best_batch.available_quantity == 20

def test_do_not_allocate_if_no_matching_sku_found():
    product_nat, order_nat, list_ol = sample_business_objects()
    order_nat.order_lines = []
    repo = repository.FakeRepository([product_nat], [order_nat,])
    uow_instance = uow.unit_of_work(repo)
    # with pytest.raises(services.InvalidOrderReference):
    results = services.allocate(
        event.AllocationRequired(
            order_reference=order_nat.order_reference,
            sku=list_ol[0].sku
        ),
        uow_instance
    )

def test_add_batch():
    product_nat, order_nat, list_ol = sample_business_objects()
    repo = repository.FakeRepository(products=[], orders=[order_nat,])
    uow_instance = uow.unit_of_work(repo)
    batch_ref=utils.random_batchref("batch")
    results = message_bus.handle(
        event=event.BatchCreated(
                sku=product_nat.sku,
                quantity=product_nat.batches[0].quantity,
                ref=batch_ref
        ),
        unit_of_work=uow_instance
    )
    inserted_batch=results[0]
    retrieved_product = repo.get(model.Product, model.Product.sku, product_nat.sku)
    assert retrieved_product.sku == product_nat.sku
    assert inserted_batch.sku == product_nat.sku