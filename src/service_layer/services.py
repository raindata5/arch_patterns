from domain import utils
import domain.model as model
import adapters.repository as repository
from typing import (
    Type,
    Union,
    Any,
)
import logging
from fastapi import (
    HTTPException,
    status
)
from domain.utils import (
    allocate_batch
)

class InvalidOrderReference(Exception):
    pass

class InvalidSkuReference(Exception):
    pass

def allocate(order_reference: model.OrderReference, sku: model.Sku, repo:Type[repository.Repository],):
    try:
        queried_order: Union[model.Order, Any] = repo.get(model.Order, model.Order.order_reference, order_reference.order_reference)
        if not queried_order:
            raise InvalidOrderReference()
        logging.info(queried_order)
        queried_order_line = queried_order.search_order_line(sku.sku)
        sku_order_line = queried_order_line.sku
        logging.info(sku_order_line)
        queried_batches = repo.list(model.Batch, model.Batch.sku, sku_order_line)
        queried_batches_list = list(queried_batches)
        if len(queried_batches_list) == 0:
            raise InvalidSkuReference()
        logging.info(queried_batches_list) # run tests twice and print skus
        best_batch = allocate_batch(queried_order, queried_batches_list)
    except ValueError as ex:
        ex.order_reference = queried_order.order_reference
        raise ex
    except (InvalidSkuReference, InvalidOrderReference, ) as ex:
        raise 
    finally:
        repo.commit()
    return best_batch


def add_batch(sku, quantity, repo:Type[repository.Repository], eta=None, arrived=None,):
    try:
        batch_ref = utils.random_batchref("NaT")
        batch_instance = model.Batch(batch_ref, sku, quantity)
        repo.add(batch_instance)
    finally :
        repo.commit()
    return batch_instance