from typing import Union
from fastapi import FastAPI
from sqlalchemy.orm import Session
from a_package.orm import engine
import a_package.repository as repository
import a_package.model as model


sql_repo = repository.SqlRepository(Session(engine))
app = FastAPI()

@app.get("/")
def read_root():
    return {"msg": "Hello World"}

@app.get("/batch/{batch_reference}")
def read_batch(batch_reference: str):
    queried_batch = sql_repo.get(model.Batch, model.Batch.reference, batch_reference)
    return queried_batch


# from enum import IntEnum
# class ShippingState(IntEnum):
#     pass
# TODO: Refactor this descriptor that is far too specific (business logic contained)














