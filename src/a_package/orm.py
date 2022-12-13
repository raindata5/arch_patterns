from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import registry, relationship, Session
from sqlalchemy.sql import func
from a_package import model
from sqlalchemy import create_engine, select
import datetime as dt


engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

mapper_registry = registry()

order_line_table=Table(
    "order_line",
    mapper_registry.metadata,
    Column(
        "id", Integer, primary_key=True, autoincrement=True
    ),
    Column(
        "sku", String(40),
    ),
    Column(
        "quantity", Integer,
    ),
    Column(
        "parent_order_reference", String(40), ForeignKey("order.id")
    ),
)

order_table=Table(
    "order",
    mapper_registry.metadata,
    Column(
        "id", Integer, primary_key=True, autoincrement=True
    ),
    Column(
        "order_reference", String(40),
    ),
    # Column(
    #     "order_lines", String(200),
    # ),
)

batch_table = Table(
    "batch",
    mapper_registry.metadata,
    Column(
        "id", Integer, primary_key=True, autoincrement=True
    ),
    Column(
        "reference", String(40), autoincrement=True
    ),
    Column(
        "sku", String(40), autoincrement=True
    ),
    Column(
        "available_quantity", Integer,
    ),
    Column(
        "quantity", Integer,
    ),
    Column(
        "eta", DateTime, nullable=False
    ),
    Column(
        "arrived", Boolean,
    ),
    Column(
        "order_reference", String(40), ForeignKey("order.id")
    ),
)


mapper_registry.map_imperatively(
    model.Order,
    order_table,
    properties={
        "order_lines": relationship(model.OrderLine, backref="order", order_by="order_line.c.parent_order_reference", uselist=True)
    }
)

mapper_registry.map_imperatively(
    model.Batch, 
    batch_table,
        properties={
        "orders": relationship(model.Order, backref="batch", order_by="order.c.id", uselist=True)
    }
)

mapper_registry.map_imperatively(
    model.OrderLine,
    order_line_table,
    # properties={
    #     "exclude_properties": ["check_order_line_match"]
    # }
)

mapper_registry.metadata.create_all(engine)

# with Session(engine) as session:
#     new_batch = model.Batch(reference='TKJ-23244', sku='RED-CHAIR', quantity=30, eta=dt.datetime.now(), arrived=False)
#     ex_order = model.Order(order_reference='TGL-23245')
#     order_lines_params = [
#         dict(sku="RED-CHAIR", quantity=10),
#         dict(sku="TASTELESS-LAMP", quantity=1)
#     ]
#     [ex_order.attach_order_line(ol) for ol in order_lines_params]
#     new_batch.allocate_stock(ex_order)
#     session.add_all([new_batch])
#     # session.commit()
#     stmt = select(model.Batch).where(model.Batch.reference == 'TKJ-23244')
#     patrick = session.scalars(stmt).one()
#     patrick: model.Batch
#     print(vars(patrick))
#     print(patrick.orders)

