from typing import (
    Union,
    Any
)
from fastapi import FastAPI
from a_package.orm import Session
import a_package.repository as repository
import a_package.model as model
from a_package.utils import (
    allocate_batch
)
import datetime as dt
from sqlalchemy import select
from pydantic import BaseModel
1
class OrderReference(BaseModel):
    order_reference : str

sql_repo = repository.SqlRepository(Session())
app = FastAPI()

@app.get("/")
def read_root():
    return {"msg": "Hello World"}

@app.get("/batch/{batch_reference}")
def read_batch(batch_reference: str):
    queried_batch = sql_repo.get(model.Batch, model.Batch.reference, batch_reference)
    return queried_batch
    
@app.post("/allocate")
def allocate_batch_ep(order_reference: OrderReference):
    queried_order: Union[model.Order, Any] = sql_repo.get(model.Order, model.Order.order_reference, order_reference.order_reference)
    
    queried_batches = sql_repo.list(model.Batch, model.Batch.sku, queried_order.order_lines[0].sku)
    queried_batches_list = list(queried_batches)
    best_batch = allocate_batch(queried_order, queried_batches_list)
    return best_batch

# from enum import IntEnum
# class ShippingState(IntEnum):
#     pass
# TODO: Refactor this descriptor that is far too specific (business logic contained)














