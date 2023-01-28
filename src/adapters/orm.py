from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import registry, relationship, sessionmaker
from sqlalchemy.sql import func
from domain import model
from sqlalchemy import create_engine, select
import datetime as dt
from sqlalchemy.pool import StaticPool
from domain import utils
from entrypoints.config import settings

# https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#using-a-memory-database-in-multiple-threads
# engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, connect_args={'check_same_thread':False},
#                     poolclass=StaticPool) 
engine = create_engine(f"postgresql://{settings.pg_oltp_api_user}:{settings.pg_oltp_api_password}@{settings.pg_oltp_api_host}:{settings.pg_oltp_api_port}", echo=True)
# engine = create_engine(f"postgresql://postgres:example@postgres", echo=True)
print(f"postgresql://{settings.pg_oltp_api_user}:{settings.pg_oltp_api_password}@{settings.pg_oltp_api_host}:{settings.pg_oltp_api_port}")
Session = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False,)
# Session().commit()
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
        "parent_order_reference", String(40), ForeignKey("order.order_reference")
    ),
)

order_table=Table(
    "order",
    mapper_registry.metadata,
    Column(
        "id", Integer, primary_key=True, autoincrement=True
    ),
    Column(
        "order_reference", String(40), unique=True
    ),
    Column(
        "batch_reference", String(200), ForeignKey("batch.reference")
    ),
)

batch_table = Table(
    "batch",
    mapper_registry.metadata,
    Column(
        "id", Integer, primary_key=True, autoincrement=True
    ),
    Column(
        "reference", String(40), autoincrement=True, unique=True
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
    # Column(
    #     "order_reference", Integer, ForeignKey("order.id")
    # ),
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

mapper_registry.metadata.create_all(
    bind=(engine)
)

if __name__ == "__main__":

    with Session() as session:
        new_batch = model.Batch(reference='TKJ-23244', sku='RED-CHAIR', quantity=30, eta=dt.datetime.now(), arrived=False)
        ex_order = model.Order(order_reference='TGL-23245')
        order_lines_params = [
            dict(sku="RED-CHAIR", quantity=10),
            dict(sku="TASTELESS-LAMP", quantity=1)
        ]
        [ex_order.attach_order_line(ol) for ol in order_lines_params]
        new_batch.allocate_stock(ex_order)
        session.add_all([new_batch])
        patrick: model.Batch
        session.commit()
        

