import redis
from service_layer import services
import json
from domain import command
import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
from service_layer import (
    message_bus,
)
from adapters import uow

# get redis params
# connect to redis
# subscribe to relevant channel
# take message and pass to message bus

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
)
def handle_change_batch_quantity(message):
    logging.debug(msg = f" Pulled {message}")

def main():
    for m in pubsub.listen():
        # message_bus.handle(m, unit_of_work=uow.unit_of_work())
        handle_change_batch_quantity(m)

if __name__ == "__main__":
    main()