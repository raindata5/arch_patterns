from adapters import (
    repository,
    uow
)
from domain import model

def tests_uow_does_not_serialize_uncommitted_edits(get_uow_context, return_unserialized_sample_data):
    uow_ins, repo = get_uow_context
    product_nat, batch_nat, order_nat, list_ol = return_unserialized_sample_data
    with uow_ins as repo:
        repo.add(product_nat)

    queried_product = repo.get(model.Product, model.Product.sku, batch_nat.sku)
    assert not queried_product

def tests_uow_serializes_committed_edits(get_uow_context, return_unserialized_sample_data):
    uow_ins, repo = get_uow_context
    product_nat, batch_nat, order_nat, list_ol = return_unserialized_sample_data
    with uow_ins as repo:
        repo.add(product_nat)
        repo.commit()

    queried_product = repo.get(model.Product, model.Product.sku, batch_nat.sku)
    assert queried_product.batches[0] == batch_nat