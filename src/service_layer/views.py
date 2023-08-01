from adapters import (
    uow
)
import adapters.repository as repository

def allocations(order_reference, unit_of_work:uow.unit_of_work,):
    stmt_sql = """
            SELECT
                *
            FROM allocation a
            WHERE 1=1
                AND order_id = :order_ref
    """
    with unit_of_work as uow:
        uow: repository.SqlRepository
        res = uow.session.execute(
            stmt_sql, 
            {"order_ref": order_reference}
        )
        return [rec for rec in res]
