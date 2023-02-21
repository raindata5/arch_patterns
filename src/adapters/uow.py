from contextlib import contextmanager
from typing import (
    Type,
    Union,
    Any,
)
import adapters.repository as repository
import logging
@contextmanager
def unit_of_work(repo:Type[repository.Repository]):
    try:
        yield repo
    except Exception as ex:
        repo.rollback()
        raise ex
    finally:
        repo.rollback()
        logging.info("Finishing transaction against DB")