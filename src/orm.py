from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import registry, relationship, Session
from sqlalchemy.sql import func
import model
from sqlalchemy import create_engine, select
import datetime as dt


engine = create_engine("sqlite://", echo=True)

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
        "quantity", Integer,
    ),
    Column(
        "eta", DateTime,
    ),
    Column(
        "arrived", Boolean,
    ),
)


mapper_registry.map_imperatively(
    model.Order,
    order_table,
    properties={
        "order_lines": relationship(model.OrderLine, backref="order", order_by="order_line.c.sku")
    }
)

mapper_registry.map_imperatively(
    model.Batch, 
    batch_table,
    #     properties={
    #     "orders": relationship(model.OrderLine, backref="batch")
    # }
)

mapper_registry.map_imperatively(model.OrderLine, order_line_table)

mapper_registry.metadata.create_all(engine)

with Session(engine) as session:
    new_batch = model.Batch(reference='TKJ-23244', sku='RED-CHAIR', quantity=30, eta=dt.datetime.now(), arrived=False)
    session.add_all([new_batch])
    session.commit()
    stmt = select(model.Batch).where(model.Batch.reference == 'TKJ-23244')
    patrick = session.scalars(stmt).one()
    print(patrick)
