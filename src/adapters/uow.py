from contextlib import contextmanager
from typing import (
    Type,
    Union,
    Any,
)
# from adapters.repository import Repository
import logging
from adapters.orm import Session

class unit_of_work:
    # def __init__(self, repo:Type[Repository]) -> None:
    def __init__(self, repo) -> None:
        self.repo = repo

    def __enter__(self):
        return self.repo

    def __exit__(self, exc_type, exc_value, exc_tracebac):
        self.repo.rollback()
        self.repo.close()
        self.repo.commit()


# @contextmanager
# def unit_of_work(repo:Type[repository.Repository]):
#     try:
#         yield repo
#     except Exception as ex:
#         repo.rollback()
#         repo.close()
#         repo.commit()
#         raise ex
#     finally:
#         logging.info("closing transaction against DB")
#         repo.rollback()
#         # while len(repo.seen) > 0:
#         #     obj_popped = repo.seen.pop()
            
#         #     [
#         #     message_bus.handle(eve) for eve in obj_popped.events
#         #     if eve
#         #     ]
#         repo.close()
#         repo.commit()