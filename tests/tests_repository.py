from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import registry, relationship, Session
from sqlalchemy.sql import func
from a_package import model
from a_package import repository
from a_package.orm import (
    engine
)
from sqlalchemy import create_engine, select
import datetime as dt
import pytest

@pytest.fixture
def get_session():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
@pytest.fixture
def sample_order_info(get_session):
    new_batch = model.Batch(reference='TKJ-23244', sku='RED-CHAIR', quantity=30, eta=dt.datetime.now(), arrived=False)
    ex_order = model.Order(order_reference='TGL-23245')
    order_lines_params = [
        dict(sku="RED-CHAIR", quantity=10),
        dict(sku="TASTELESS-LAMP", quantity=1)
    ]
    order_lines = [ex_order.attach_order_line(order_lines_param) for order_lines_param in order_lines_params]
    get_session.add_all(
        [
            new_batch, ex_order, order_lines[0], order_lines[1]
        ]
    )
    get_session.commit()
    return new_batch, ex_order, order_lines_params

def test_serialization_of_batch(get_session, sample_order_info):
    session: Session = get_session
    sql_repo = repository.SqlRepository(session)
    new_batch, ex_order, order_lines_params = sample_order_info
    sql_repo.add(new_batch)
    sql_repo.commit()
    stmt = select(model.Batch).where(model.Batch.reference == new_batch.reference)
    stored_batch = session.scalars(stmt).one()
    assert stored_batch == new_batch

def test_get_a_batch(get_session, sample_order_info):
    session: Session = get_session
    sql_repo = repository.SqlRepository(session)
    new_batch, ex_order, order_lines_params = sample_order_info
    queried_batch = sql_repo.get(model.Batch, model.Batch.reference, new_batch.reference)
    assert queried_batch == new_batch
    

    