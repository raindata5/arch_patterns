from domain import model
from adapters import (
    uow,
    repository
)
import datetime as dt
import pytest

def return_sample_order_info():
    new_batch = model.Batch(reference='TKJ-23244', sku='RED-CHAIR', quantity=30, arrived=False)
    ex_order = model.Order(order_reference='TGL-23245')
    order_lines_params = [
        dict(sku="RED-CHAIR", quantity=10),
        dict(sku="TASTELESS-LAMP", quantity=1)
    ]
    return new_batch, ex_order, order_lines_params
    
def get_uow():
    repo_fake = repository.FakeRepository([], [])
    return uow.unit_of_work, repo_fake

@pytest.fixture(scope="function")
def sample_order_info():
    new_batch, ex_order, order_lines_params = return_sample_order_info()
    order_lines = [ex_order.attach_order_line(order_lines_param) for order_lines_param in order_lines_params]
    new_batch.allocate_stock(ex_order)

    repo_fake = repository.FakeRepository([new_batch], [ex_order])
    return uow.unit_of_work, repo_fake

def test_serialization_of_batch():
    uow_ins, repo_fake = get_uow()
    new_batch, ex_order, order_lines_params = return_sample_order_info()
    with uow_ins(repo_fake) as repo:
        repo.add(new_batch)
        repo.commit()
    assert repo_fake.committed

    with uow_ins(repo_fake) as repo:
        batch_queried = repo.get(model.Batch, model.Batch.reference, new_batch.reference)

    assert new_batch == batch_queried

def test_get_a_batch(sample_order_info):
    uow_ins, repo_fake = sample_order_info
    new_batch, ex_order, order_lines_params = return_sample_order_info()
    with uow_ins(repo_fake) as repo:
        queried_batch = repo.get(model.Batch, model.Batch.reference, new_batch.reference)
        
    assert queried_batch == new_batch
    assert queried_batch.sku == new_batch.sku
    assert queried_batch.quantity == new_batch.quantity
    assert queried_batch.available_quantity == (new_batch.available_quantity - 10)
    queried_order_line = queried_batch.orders[0].order_lines[0]
    assert  "RED-CHAIR" == queried_order_line.sku
    assert  10 == queried_order_line.quantity
    assert queried_batch.eta == new_batch.eta
    assert queried_batch.arrived == new_batch.arrived


    

