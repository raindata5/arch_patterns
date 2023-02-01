import logging
from typing import (
    Union,
    Any
)

from fastapi import (
    FastAPI,
    status,
    HTTPException
)

from adapters.orm import Session
import adapters.repository as repository
import domain.model as model
from service_layer.services import (
    allocate,
    InvalidOrderReference,
    InvalidSkuReference,
    add_batch
)
from domain.utils import (
    allocate_batch
)
import datetime as dt
from sqlalchemy import select



logger = logging.getLogger()
logger.setLevel(logging.INFO)
sql_repo = repository.SqlRepository(Session())
app = FastAPI()

@app.get("/")
def read_root():
    return {"msg": "Hello World"}

@app.get("/batch/{batch_reference}")
def read_batch(batch_reference: str):
    queried_batch = sql_repo.get(model.Batch, model.Batch.reference, batch_reference)
    sql_repo.commit()
    return queried_batch

@app.post("batches",  status_code=status.HTTP_201_CREATED,)
def add_batch_ep(batch_info: model.PreBatchInstance):
    inserted_batch = add_batch(repo=sql_repo, **batch_info)
    return inserted_batch

@app.post("/allocate", status_code=status.HTTP_201_CREATED, )
def allocate_batch_ep(order_reference: model.OrderReference, sku: model.Sku):
    #TODO: Allow the client to specify a sku
    try:
        best_batch = allocate(order_reference, sku, sql_repo)
    except InvalidOrderReference as ex :
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=F"No order found with the following order_reference {order_reference}")
    except InvalidSkuReference as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=F"No batch found with the following {sku.sku}")
    except ValueError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=F"order:{ex.order_reference} not containing an order_line with the following sku: {sku.sku}")
    return best_batch


    # try:
    #     queried_order: Union[model.Order, Any] = sql_repo.get(model.Order, model.Order.order_reference, order_reference.order_reference)
    #     if not queried_order:
    #         raise HTTPException(status.HTTP_404_NOT_FOUND, detail=F"No order found with the following order_reference {order_reference}")
    #     logging.info(queried_order)
    #     queried_order_line = queried_order.search_order_line(sku.sku)
    #     sku_order_line = queried_order_line.sku
    #     logging.info(sku_order_line)
    #     queried_batches = sql_repo.list(model.Batch, model.Batch.sku, sku_order_line)
    #     queried_batches_list = list(queried_batches)
    #     if len(queried_batches_list) == 0:
    #         raise HTTPException(status.HTTP_404_NOT_FOUND, detail=F"No batch found with the following {sku_order_line}")
    #     logging.info(queried_batches_list) # run tests twice and print skus
    #     best_batch = allocate_batch(queried_order, queried_batches_list)
    # except HTTPException as ex:    
    #     raise
    # except ValueError as ex:
    #     raise HTTPException(status.HTTP_404_NOT_FOUND, detail=F"order:{queried_order.order_reference} not containing an order_line with the following sku: {sku.sku}")
    # finally:
    #     sql_repo.commit()
    # return best_batch

# from enum import IntEnum
# class ShippingState(IntEnum):
#     pass
# TODO: Refactor this descriptor that is far too specific (business logic contained)














