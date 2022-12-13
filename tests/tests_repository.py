from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import registry, relationship, Session
from sqlalchemy.sql import func
from a_package import model
from a_package import repository
from a_package.orm import (
    engine
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, select
import datetime as dt
import pytest

session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
@pytest.fixture(scope="function")
def get_session():
    # db = Session(engine)
    db = session_maker()
    # try:
    yield db
    # finally:
    db.rollback()
    db.close()
        
@pytest.fixture(scope="function")
def get_sql_repository(get_session):
    session: Session = get_session
    sql_repo = repository.SqlRepository(session)
    return sql_repo


def return_sample_order_info():
    new_batch = model.Batch(reference='TKJ-23244', sku='RED-CHAIR', quantity=30, arrived=False)
    ex_order = model.Order(order_reference='TGL-23245')
    order_lines_params = [
        dict(sku="RED-CHAIR", quantity=10),
        dict(sku="TASTELESS-LAMP", quantity=1)
    ]
    return new_batch, ex_order, order_lines_params
    
@pytest.fixture(scope="function")
def sample_order_info(get_sql_repository):
    new_batch, ex_order, order_lines_params = return_sample_order_info()
    order_lines = [ex_order.attach_order_line(order_lines_param) for order_lines_param in order_lines_params]
    new_batch.allocate_stock(ex_order)
    get_sql_repository.session.add_all(
        [
            new_batch,# ex_order, order_lines[0], order_lines[1]
        ]
    )
    get_sql_repository.session.commit()
    return get_sql_repository



def test_serialization_of_batch( get_sql_repository):
    sql_repo = get_sql_repository
    new_batch, ex_order, order_lines_params = return_sample_order_info()
    sql_repo.add(new_batch)
    sql_repo.commit()
    stmt = select(model.Batch).where(model.Batch.reference == new_batch.reference)
    stored_batch = sql_repo.session.scalars(stmt).one()
    sql_repo.session.expire_all()
    assert stored_batch == new_batch
    sql_repo.session.delete(stored_batch)
    sql_repo.commit()

def test_get_a_batch(sample_order_info):
    sql_repo = sample_order_info
     
    new_batch, ex_order, order_lines_params = return_sample_order_info()
    queried_batch = sql_repo.get(model.Batch, model.Batch.reference, new_batch.reference)
    assert queried_batch == new_batch
    assert queried_batch.sku == new_batch.sku
    assert queried_batch.quantity == new_batch.quantity
    assert queried_batch.available_quantity == (new_batch.available_quantity - 10)
    queried_order_line = queried_batch.orders[0].order_lines[0]
    assert  "RED-CHAIR" == queried_order_line.sku
    assert  10 == queried_order_line.quantity
    assert queried_batch.eta == new_batch.eta
    assert queried_batch.arrived == new_batch.arrived


    

