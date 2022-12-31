from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import registry, relationship, sessionmaker
from sqlalchemy.sql import func
from a_package import model
from sqlalchemy import create_engine, select
import datetime as dt
from sqlalchemy.pool import StaticPool
from a_package.orm import Session
import a_package.repository as repository
import pytest


@pytest.fixture
def get_sql_repo():
    sql_repo = repository.SqlRepository(Session())
    return sql_repo

@pytest.fixture
def inserted_sample_data(get_sql_repo):
    # with Session() as session:
    #     new_batch = model.Batch(reference='TKJ-23244', sku='RED-CHAIR', quantity=30, eta=dt.datetime.now(), arrived=False)
    #     ex_order = model.Order(order_reference='TGL-23245')
    #     order_lines_params = [
    #         dict(sku="RED-CHAIR", quantity=10),
    #         dict(sku="TASTELESS-LAMP", quantity=1)
    #     ]
    #     [ex_order.attach_order_line(ol) for ol in order_lines_params]
    #     new_batch.allocate_stock(ex_order)
    #     session.add_all([new_batch])
    #     stmt = select(model.Batch).where(model.Batch.reference == 'TKJ-23244')
    #     patrick = session.scalars(stmt).one()
    #     patrick: model.Batch
    #     print(vars(patrick))
    #     print(patrick.orders)
    #     session.commit()
    pass