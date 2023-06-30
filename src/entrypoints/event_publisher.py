import redis
import logging
import json
from dataclasses import asdict
# get redis params
# connect to redis
# subscribe to relevant channel
# take message and pass to message bus

r = redis.Redis(
    host='redis',
    port=6379
)

def publish(channel:str, message):
    logging.info(f"publishing {message} to channel:{channel}")
    r.publish(channel=channel, message=json.dumps(asdict(message)))