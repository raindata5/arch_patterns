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
    product_nat = model.Product(sku=new_batch.sku, batches=[new_batch])
    order_lines_params = [
        dict(sku="RED-CHAIR", quantity=10),
        dict(sku="TASTELESS-LAMP", quantity=1)
    ]
    return product_nat, new_batch, ex_order, order_lines_params
    
def get_uow():
    repo_fake = repository.FakeRepository([], [])
    return uow.unit_of_work, repo_fake

@pytest.fixture(scope="function")
def sample_order_info():
    product_nat, new_batch, ex_order, order_lines_params = return_sample_order_info()
    order_lines = [ex_order.attach_order_line(order_lines_param) for order_lines_param in order_lines_params]
    new_batch.allocate_stock(ex_order)

    repo_fake = repository.FakeRepository([product_nat], [ex_order])
    return uow.unit_of_work, repo_fake

def test_serialization_of_batch():
    uow_ins, repo_fake = get_uow()
    product_nat, new_batch, ex_order, order_lines_params = return_sample_order_info()
    with uow_ins(repo_fake) as repo:
        repo.add(product_nat)
        repo.commit()
    assert repo_fake.committed

    with uow_ins(repo_fake) as repo:
        queried_product = repo.get(model.Product, model.Product.sku, new_batch.sku)

    assert new_batch == queried_product.batches[0]

def test_get_a_batch(sample_order_info):
    uow_ins, repo_fake = sample_order_info
    product_nat, new_batch, ex_order, order_lines_params = return_sample_order_info()
    with uow_ins(repo_fake) as repo:
        queried_product = repo.get(model.Product, model.Product.sku, new_batch.sku)
        
    assert queried_product.batches[0] == new_batch
    assert queried_product.batches[0].sku == new_batch.sku
    assert queried_product.batches[0].quantity == new_batch.quantity
    assert queried_product.batches[0].available_quantity == (new_batch.available_quantity - 10)
    queried_order_line = queried_product.batches[0].orders[0].order_lines[0]
    assert  "RED-CHAIR" == queried_order_line.sku
    assert  10 == queried_order_line.quantity
    assert queried_product.batches[0].eta == new_batch.eta
    assert queried_product.batches[0].arrived == new_batch.arrived


    

