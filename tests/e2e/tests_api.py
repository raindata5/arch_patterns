from fastapi.testclient import TestClient
from entrypoints.main import app
import requests
from domain import model
from typing import (
    Tuple,
    List,
    Dict
)
from entrypoints.config import settings
import json

client = TestClient(app)

def test_read_main_root(get_sql_repo):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"msg": "Hello World"}
    print("Got the home page")

def test_get_batch(return_base_sample_data):
    # queried_batch = client.get("/batch", params="TKJ-23244")
    batch_nat, order_nat, order_lines_params = return_base_sample_data
    batch_nat: model.Batch
    order_nat: model.Order
    data = requests.get(
        F"{settings.api_url}/batch/{batch_nat.reference}",

    )
    data.json()["reference"] == batch_nat.reference

def test_allocate_batch(return_base_sample_data):
    batch_nat, order_nat, list_ol = return_base_sample_data
    batch_nat: model.Batch
    order_nat: model.Order

    list_ol: List[model.OrderLine]
    order_nat_ref = order_nat.order_reference
    sku_body = dict(sku=list_ol[0].sku)
    order_ref_body = dict(order_reference=order_nat_ref,)
    data_sku_order = dict(order_reference=order_ref_body, sku=sku_body)
    res = requests.post(f"{settings.api_url}/allocate", json=data_sku_order)
    assert res.status_code == 201
    assert res.json()["reference"] == batch_nat.reference
    assert res.json()["available_quantity"] == batch_nat.available_quantity - list_ol[0].quantity

# TODO: Migrate the following tests to service layer

def test_allocate_stock_returns_404_no_stock(return_base_sample_data, return_serialized_order):
    batch_nat, order_nat, list_ol = return_base_sample_data
    order_nat, list_ol = return_serialized_order
    batch_nat: model.Batch
    order_nat: model.Order
    list_ol: List[model.OrderLine]
    order_nat_ref = order_nat.order_reference
    sku_body = dict(sku=list_ol[0].sku)
    order_ref_body = dict(order_reference=order_nat_ref,)
    data_sku_order = dict(order_reference=order_ref_body, sku=sku_body)

    res = requests.post(f"{settings.api_url}/allocate", json=data_sku_order)
    assert res.status_code == 404
    res_text= res.text
    detail=F"No batch found with the following {list_ol[0].sku}"
    text ={"detail":detail}
    text_str = json.dumps(text, separators=(',', ':'))
    assert res_text == text_str


def test_allocate_stock_returns_404_no_sku_found(return_base_sample_data, return_serialized_order):
    batch_nat, order_nat, list_ol = return_base_sample_data
    order_nat_02, list_ol_02 = return_serialized_order
    batch_nat: model.Batch
    order_nat: model.Order
    list_ol: List[model.OrderLine]
    order_nat_ref = order_nat.order_reference
    sku_mod = list_ol_02[0].sku + "fake_nat_sku"
    sku_body = dict(sku=sku_mod)
    order_ref_body = dict(order_reference=order_nat_ref,)
    data_sku_order = dict(order_reference=order_ref_body, sku=sku_body)

    res = requests.post(f"{settings.api_url}/allocate", json=data_sku_order)
    assert res.status_code == 404
    res_text= res.text
    detail=F"order:{order_nat_ref} not containing an order_line with the following sku: {sku_mod}"
    text ={"detail":detail}
    text_str = json.dumps(text, separators=(',', ':'))
    assert res_text == text_str

def test_add_batch_returns_201(get_sql_repo):
    batch_body = dict(
        sku="a_sku",
        quantity=30,
        arrived=False
    )    
    res = requests.post(f"{settings.api_url}/batches", json=batch_body)
    assert res.status_code == 201
    assert res.json()["arrived"] == False
    assert res.json()["available_quantity"] == batch_body["quantity"]
    assert res.json()["sku"] == batch_body["sku"]
