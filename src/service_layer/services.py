from domain import utils
from domain import event as eve
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
def allocate(event: eve.AllocationRequired, unit_of_work:uow.unit_of_work,):
    with unit_of_work as uow:   
        try:
            queried_order: Union[model.Order, Any] = uow.get(model.Order, model.Order.order_reference, event.order_reference)
            if not queried_order:
                raise InvalidOrderReference()
            logging.info(queried_order)
            queried_order_line = queried_order.search_order_line(event.sku)
            sku_order_line = queried_order_line.sku
            logging.info(sku_order_line)
            product: model.Product = uow.get(model.Product, model.Product.sku, sku_order_line)

            if not product:
                raise InvalidSkuReference()
            logging.info(product.batches) # run tests twice and print skus
            
            product.version += 1
            best_batch = product.allocate(queried_order)
            if not best_batch:
                product.events.append(eve.OutOfStockEvent(sku=event.sku))
                uow.add(product)
        except (InvalidSkuReference, InvalidOrderReference, ) as ex:
            raise ex
        uow.commit()
    return best_batch


def add_batch(event: eve.BatchCreated, unit_of_work:uow.unit_of_work,):
    batch_ref = event.ref or utils.random_batchref("batch")
    eta= event.eta or dt.datetime(9999,1,1)
    arrived=event.arrived or False
    with unit_of_work as uow:
        product = uow.get(model.Product, model.Product.sku, event.sku)
        if product is None:
            product = model.Product(sku=event.sku, batches=[])
            print(vars(product))
            uow.add(product)
        batch_instance = model.Batch(batch_ref, event.sku, event.quantity, eta=eta, arrived=arrived)
        product.batches.append(batch_instance)
        uow.commit()
    return batch_instance