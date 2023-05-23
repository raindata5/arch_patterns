from contextlib import contextmanager
from typing import (
    Type,
    Union,
    Any,
)
import adapters.repository as repository
import logging
from service_layer import message_bus
@contextmanager
def unit_of_work(repo:Type[repository.Repository]):
    try:
        yield repo
    except Exception as ex:
        repo.rollback()
        repo.close()
        repo.commit()
        raise ex
    finally:
        logging.info("closing transaction against DB")
        repo.rollback()
        while len(repo.seen) > 0:
            obj_popped = repo.seen.pop()
            
            [
            message_bus.handle(eve) for eve in obj_popped.events
            if eve
            ]
        repo.close()
        repo.commit()