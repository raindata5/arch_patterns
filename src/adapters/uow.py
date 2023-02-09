from contextlib import contextmanager
from typing import (
    Type,
    Union,
    Any,
)
import adapters.repository as repository

@contextmanager
def unit_of_work(repo:Type[repository.Repository]):
    try:
        yield repo
    finally:
        repo.rollback()