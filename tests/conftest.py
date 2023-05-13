from domain import model
import datetime as dt
import pytest
from domain import utils
import logging
import psycopg2
from sqlalchemy.orm import sessionmaker
from domain import model
from sqlalchemy import create_engine
import datetime as dt
from domain import utils
from entrypoints.config import settings
from adapters.orm import Session
from adapters import (
    uow,
    repository
)
from typing import (
    List,
)

engine = create_engine(f"postgresql://{settings.pg_oltp_api_user}:{settings.pg_oltp_api_password}@{settings.pg_oltp_api_host}:{settings.pg_oltp_api_port}", echo=True,)

print(f"postgresql://{settings.pg_oltp_api_user}:{settings.pg_oltp_api_password}@{settings.pg_oltp_api_host}:{settings.pg_oltp_api_port}")
Session = sessionmaker(bind=engine, expire_on_commit=False)


logger = logging.getLogger()
logger.setLevel(logging.INFO)

@pytest.fixture()
def get_sql_repo():
    with open("/architecture_patterns/postgres-table-truncates.sql") as sql_file: 
        ps_conn = psycopg2.connect("postgresql://postgres:example@postgres:5432",)
        ps_cursor = ps_conn.cursor()

        ps_conn.commit()
        
        ps_cursor.execute(sql_file.read())

        ps_conn.commit()
        ps_cursor.close()
        ps_conn.close()

@pytest.fixture()
def get_uow_context(get_sql_repo):
    repo=repository.SqlRepository(Session())
    uow_ins = uow.unit_of_work(repo)
    return uow_ins, repo

@pytest.fixture
def return_unserialized_sample_data():
    sku_ref_natty, sku_ref_natty_01 = utils.random_sku("NaTTY"), utils.random_sku("NaTTY_01")
    batch_ref_nat = utils.random_batchref("NaT")
    order_ref_nat = utils.random_orderid("nat_order")

    product_nat = model.Product(sku=sku_ref_natty, batches=[])
    batch_nat = model.Batch(reference=batch_ref_nat, sku=sku_ref_natty, quantity=30, eta=dt.datetime.now(), arrived=False)
    order_nat = model.Order(order_reference=order_ref_nat)
    product_nat.batches.append(batch_nat)
    order_lines_params = [
        dict(sku=sku_ref_natty, quantity=10),
        dict(sku=sku_ref_natty_01, quantity=1)
]
    list_ol = [order_nat.attach_order_line(ol) for ol in order_lines_params]
    
    batch_nat: model.Batch
    order_nat: model.Order
    list_ol: List[model.OrderLine]
    return batch_nat, order_nat, list_ol

@pytest.fixture()
def return_base_sample_data(get_sql_repo):
    with Session() as session:
        sku_ref_natty, sku_ref_natty_01 = utils.random_sku("NaTTY"), utils.random_sku("NaTTY_01")
        batch_ref_nat = utils.random_batchref("NaT")
        order_ref_nat = utils.random_orderid("nat_order")

        product_nat = model.Product(sku=sku_ref_natty, batches=[])
        batch_nat = model.Batch(reference=batch_ref_nat, sku=sku_ref_natty, quantity=30, eta=dt.datetime.now(), arrived=False)
        order_nat = model.Order(order_reference=order_ref_nat)
        order_lines_params = [
            dict(sku=sku_ref_natty, quantity=10),
            dict(sku=sku_ref_natty_01, quantity=1)
    ]
        product_nat.batches.append(batch_nat)
        list_ol = [order_nat.attach_order_line(ol) for ol in order_lines_params]
        # new_batch.allocate_stock(ex_order)
        # session.add_all([batch_nat, order_nat, product_nat])  
        session.add_all([ order_nat, product_nat])  
        session.commit()
    return batch_nat, order_nat, list_ol

@pytest.fixture
def return_serialized_order(get_sql_repo):
    with Session() as session:
        sku_ref_natty, sku_ref_natty_01 = utils.random_sku("NaTTY"), utils.random_sku("NaTTY_01")

        order_ref_nat = utils.random_orderid("nat_order")

        order_nat = model.Order(order_reference=order_ref_nat)
        order_lines_params = [
            dict(sku=sku_ref_natty, quantity=10),
            dict(sku=sku_ref_natty_01, quantity=1)
    ]
        list_ol = [order_nat.attach_order_line(ol) for ol in order_lines_params]
        session.add_all([order_nat,])  
        session.commit()
    return order_nat, list_ol