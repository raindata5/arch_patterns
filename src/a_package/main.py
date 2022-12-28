from typing import Union
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/batch/{batch_reference}")
def read_batch(batch_reference: str):
    return batch_reference


# from enum import IntEnum
# class ShippingState(IntEnum):
#     pass
# TODO: Refactor this descriptor that is far too specific (business logic contained)














