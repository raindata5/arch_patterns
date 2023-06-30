import redis
from service_layer import services
import json
from domain import command
import logging
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
    "change_batch_quantity"
)
def handle_change_batch_quantity(message):
    logging.info(msg = f" Pulled {message}")

def main():
    for m in pubsub.listen():
        handle_change_batch_quantity(m)

if __name__ == "__main__":
    main()