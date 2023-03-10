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
from adapters import (
    uow
)
import datetime as dt

class InvalidOrderReference(Exception):
    pass

class InvalidSkuReference(Exception):
    pass
def allocate(order_reference: model.OrderReference, sku: model.Sku, unit_of_work:uow.unit_of_work,):
    with unit_of_work as uow:
        
        try:
            queried_order: Union[model.Order, Any] = uow.get(model.Order, model.Order.order_reference, order_reference.order_reference)
            if not queried_order:
                raise InvalidOrderReference()
            logging.info(queried_order)
            queried_order_line = queried_order.search_order_line(sku.sku)
            sku_order_line = queried_order_line.sku
            logging.info(sku_order_line)
            queried_batches = uow.list(model.Batch, model.Batch.sku, sku_order_line)
            queried_batches_list = list(queried_batches)
            if len(queried_batches_list) == 0:
                raise InvalidSkuReference()
            logging.info(queried_batches_list) # run tests twice and print skus
            best_batch = allocate_batch(queried_order, queried_batches_list)
        except ValueError as ex:
            ex.order_reference = queried_order.order_reference
            raise ex
        except (InvalidSkuReference, InvalidOrderReference, ) as ex:
            raise ex
        uow.commit()
    return best_batch


def add_batch(sku, quantity, unit_of_work:uow.unit_of_work, eta=None, arrived=None, ref=None):
    batch_ref = ref or utils.random_batchref("batch")
    eta= eta or dt.datetime(9999,1,1),
    arrived=arrived or False
    with unit_of_work as uow:
        batch_instance = model.Batch(batch_ref, sku, quantity, eta=eta, arrived=arrived)
        uow.add(batch_instance)
        uow.commit()
    return batch_instance