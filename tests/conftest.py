from a_package import model
import datetime as dt
from a_package.orm import Session
import a_package.repository as repository
import pytest
from a_package import utils

@pytest.fixture
def get_sql_repo():
    sql_repo = repository.SqlRepository(Session())
    return sql_repo

@pytest.fixture
def return_addi_sample_data(get_sql_repo):
    with Session() as session:
        sku_ref_natty, sku_ref_natty_01 = utils.random_sku("NaTTY"), utils.random_sku("NaTTY_01")
        batch_ref_nat = utils.random_batchref("NaT")
        order_ref_nat = utils.random_orderid("nat_order")

        batch_nat = model.Batch(reference=batch_ref_nat, sku=sku_ref_natty, quantity=30, eta=dt.datetime.now(), arrived=False)
        order_nat = model.Order(order_reference=order_ref_nat)
        order_lines_params = [
            dict(sku=sku_ref_natty, quantity=10),
            dict(sku=sku_ref_natty_01, quantity=1)
    ]
        [order_nat.attach_order_line(ol) for ol in order_lines_params]
        # new_batch.allocate_stock(ex_order)
        session.add_all([batch_nat, order_nat,])
    #     stmt = select(model.Batch).where(model.Batch.reference == 'TKJ-23244')
    #     patrick = session.scalars(stmt).one()
    #     patrick: model.Batch
    #     print(vars(patrick))
    #     print(patrick.orders)
    #     session.commit()
    batch_nat, order_nat, order_lines_params