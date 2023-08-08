from adapters import (
    uow
)
import adapters.repository as repository
from sqlalchemy import text
import logging

def allocations(order_reference, unit_of_work:uow.unit_of_work,):
    stmt_sql = """
            SELECT
                o.order_reference,
                b.reference batch_reference
            FROM "order" o
            LEFT JOIN "allocation" a
                ON o.id = a.order_id
            LEFT JOIN "batch" b
                ON a.batch_id = b.id
            WHERE 1=1
                AND o.order_reference = :order_ref
    """
    # stmt_sql = """
    #         SELECT 1
    # """
    with unit_of_work as uow:
        uow: repository.SqlRepository
        res = uow.session.execute(
            text(stmt_sql), 
            {"order_ref": order_reference}
        )
        # return [row.batch_id for row in res]
        res_all = res.all()
        logging.info(res_all)        
        return [res._asdict() for res in res_all]
