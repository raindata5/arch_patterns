from fastapi.testclient import TestClient
from a_package.main import app
import requests
from a_package import model
from typing import (
    Tuple,
    List,
    Dict
)
client = TestClient(app)


def test_read_main_root():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"msg": "Hello World"}
    print("Got the home page")

def test_get_batch():
    # queried_batch = client.get("/batch", params="TKJ-23244")
    data = requests.get(
        "http://127.0.0.1:8000/batch/TKJ-23244",
    )
    print(data.json())

def test_allocate_batch(return_addi_sample_data):
    batch_nat, order_nat, order_lines_params = return_addi_sample_data()
    batch_nat: model.Batch
    order_nat: model.Order
    order_lines_params: List[Dict]
    order_nat_ref = order_nat.order_reference
    data_order = dict(order_ref=order_nat_ref)
    res = requests.post("/allocate", data=data_order)
    assert res.status_code == 201
    assert res.json()["batch_ref"] == batch_nat.reference