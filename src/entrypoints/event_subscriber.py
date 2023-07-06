import redis
from service_layer import services
import json
from domain import (
    event,
    command
)
import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
from service_layer import (
    message_bus,
)
from adapters import uow
from sqlalchemy import create_engine
from entrypoints.config import settings
from sqlalchemy.orm import sessionmaker
import adapters.repository as repository
from adapters.orm import (
    mapper_registry
)

engine = create_engine(f"postgresql://{settings.pg_oltp_api_user}:{settings.pg_oltp_api_password}@{settings.pg_oltp_api_host}:{settings.pg_oltp_api_port}", echo=True)
# engine = create_engine(f"postgresql://postgres:example@postgres", echo=True)
print(f"postgresql://{settings.pg_oltp_api_user}:{settings.pg_oltp_api_password}@{settings.pg_oltp_api_host}:{settings.pg_oltp_api_port}")
Session = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False,)
mapper_registry.metadata.create_all(
    bind=(engine)
)
repo = repository.SqlRepository(Session())
# get redis params
# connect to redis
# subscribe to relevant channel
# take message and pass to message bus
CHANNELS = {
    'allocate': command.Allocate,
    'change_batch_quantity': command.ChangeBatchQuantity,
    'order_allocated': event.Allocated
}

r = redis.Redis(
    host='redis',
    port=6379
)

pubsub = r.pubsub(
    ignore_subscribe_messages=True
)
pubsub.subscribe(
    "change_batch_quantity",
    "allocate",
    "order_allocated"
)
def handle_change_batch_quantity(message):
    logging.debug(msg = f" Pulled {message}")

def main():
    for m in pubsub.listen():
        message_dict = m
        message_channel: bytes = message_dict["channel"]
        message_data: bytes = message_dict["data"]
        message_type = CHANNELS.get(message_channel.decode()) 
        message_obj_dict = json.loads(message_data)
        message_obj = message_type(**message_obj_dict)
        message_bus.handle(message_obj, unit_of_work=uow.unit_of_work(repo))


        # handle_change_batch_quantity(m)

if __name__ == "__main__":
    main()