from fastapi.testclient import TestClient
from entrypoints.main import app
from entrypoints.event_publisher import publish
import requests
from typing import (
    Tuple,
    List,
    Dict
)
from entrypoints.config import settings
import json
from domain import (
    model,
    event,
    command,
    utils,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from entrypoints.config import settings
from adapters import (
    repository
)
import time

engine = create_engine(f"postgresql://{settings.pg_oltp_api_user}:{settings.pg_oltp_api_password}@{settings.pg_oltp_api_host}:{settings.pg_oltp_api_port}", echo=True,)

print(f"postgresql://{settings.pg_oltp_api_user}:{settings.pg_oltp_api_password}@{settings.pg_oltp_api_host}:{settings.pg_oltp_api_port}")
Session = sessionmaker(bind=engine, expire_on_commit=True)


client = TestClient(app)

def test_read_main_root(get_sql_repo):
    res = client.get("/")
    assert res.status_code == 200
    res_content = res.content
    res_content_str = str(res_content)
    assert "click me Mr." in res_content_str


def test_get_batch(return_base_sample_data):
    product_nat, order_nat, order_lines_params = return_base_sample_data
    product_nat: model.Product
    batch_nat = product_nat.batches[0]
    order_nat: model.Order
    data = requests.get(
        F"{settings.api_url}/batch/{batch_nat.reference}",
    )
    data_content = data.content
    data_content_str = str(data_content)
    assert batch_nat.reference in data_content_str

def test_allocate_batch(return_base_sample_data):
    product_nat, order_nat, list_ol = return_base_sample_data
    product_nat: model.Product
    batch_nat = product_nat.batches[0]
    order_nat: model.Order

    list_ol: List[model.OrderLine]
    order_nat_ref = order_nat.order_reference
    sku_body = dict(sku=list_ol[0].sku)
    order_ref_body = dict(order_reference=order_nat_ref,)
    data_sku_order = dict(order_reference=order_ref_body, sku=sku_body)
    res = requests.post(f"{settings.api_url}/allocate", json=data_sku_order)
    res_json = res.json()
    assert res.status_code == 201
    assert res_json["reference"] == product_nat.batches[0].reference
    assert res_json["available_quantity"] == product_nat.batches[0].available_quantity - list_ol[0].quantity

# TODO: Migrate the following tests to service layer

def test_allocate_stock_returns_404_no_stock(return_base_sample_data, return_serialized_order):
    product_nat, order_nat, list_ol = return_base_sample_data
    order_nat, list_ol = return_serialized_order
    batch_nat: model.Product
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
    product_nat, order_nat, list_ol = return_base_sample_data
    order_nat_02, list_ol_02 = return_serialized_order
    product_nat: model.Product
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
    batch_info = dict(
        sku="a_sku",
        quantity=30,
        arrived=False,
        eta=None
    )    
    res = requests.post(f"{settings.api_url}/batches", json=batch_info)
    assert res.status_code == 200



def test_allocate_from_channel(return_base_sample_data,):
    product_nat, order_nat, list_ol = return_base_sample_data
    product_nat: model.Product
    order_nat: model.Order
    list_ol: List[model.OrderLine]

    command_allocate = command.Allocate(
        order_reference=order_nat.order_reference,
        sku=product_nat.sku
    )
    publish(
        channel="allocate",
        message=command_allocate
    )
    repo=repository.SqlRepository(Session())

    retreived_product = repo.get(model.Product, model.Product.sku, product_nat.sku)
    reference_batch = retreived_product.batches[0].reference
    retreived_batch = retreived_product.get_batch(reference_batch)

    assert retreived_batch.available_quantity == 20



def test_change_batch_quantity(return_base_sample_data):
    product_nat, order_nat, list_ol = return_base_sample_data
    product_nat: model.Product
    order_nat: model.Order
    list_ol: List[model.OrderLine]

    command_allocate = command.Allocate(
        order_reference=order_nat.order_reference,
        sku=product_nat.sku
    )
    
    publish(
        channel="allocate",
        message=command_allocate
    )

    time.sleep(5)
    command_cbq = command.ChangeBatchQuantity(
        batch_reference=product_nat.batches[0].reference,
        new_quantity_offset=-30,
        sku=product_nat.batches[0].sku
    )

    publish(
        channel="change_batch_quantity",
        message=command_cbq
    )

    repo=repository.SqlRepository(Session())

    time.sleep(5)
    retreived_product = repo.get(model.Product, model.Product.sku, product_nat.sku)
    reference_batch = retreived_product.batches[0].reference
    retreived_batch = retreived_product.get_batch(reference_batch)

    assert retreived_batch.available_quantity == 0


    # retreived_product = repo.get(model.Order, model.Product.sku, product_nat.sku)
    # res = requests.post(f"{settings.api_url}/change_batch_quantity", json=None)
    # res_json = res.json()
    # assert res.status_code == 201
    # assert res.json()


def test_get_allocations_for_order(return_base_sample_data):
    product_nat, order_nat, list_ol = return_base_sample_data
    product_nat: model.Product
    order_nat: model.Order
    list_ol: List[model.OrderLine]

    order_nat_ref = order_nat.order_reference
    sku_body = dict(sku=list_ol[0].sku)
    order_ref_body = dict(order_reference=order_nat_ref,)
    data_sku_order = dict(order_reference=order_ref_body, sku=sku_body)
    res = requests.post(f"{settings.api_url}/allocate", json=data_sku_order)

    data = requests.get(
        F"{settings.api_url}/allocations/{order_nat_ref}",
    )
    data_json = data.json()
    assert len(data_json["allocations"]) == 1
    assert data_json["allocations"][0]['batch_reference'] == product_nat.batches[0].reference
