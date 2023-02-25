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
        repo.close()
        repo.commit()
        raise ex
    finally:
        logging.info("closing transaction against DB")
        repo.rollback()
        repo.close()
        repo.commit()