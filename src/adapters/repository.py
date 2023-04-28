import abc
from domain import model
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import (
    List,
)

class Repository(abc.ABC):

    @abc.abstractmethod
    def add(self, object):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, id: str) -> model.Batch: 
        raise NotImplementedError


class SqlRepository(Repository):
    
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, object):
        self.session.add(object)
        return object

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
        self.session.close()

    def close(self):
        self.session.close()

    def get(self, class_object,class_object_column, reference):
        stmt = select(class_object).where(class_object_column == reference)
        result=self.session.scalars(statement=stmt)
        self.commit()
        return result.first()

    def list(self, class_object,class_object_column, filter):
        stmt = select(class_object).where(class_object_column == filter)
        result=self.session.scalars(statement=stmt)
        # self.session.query().with_for_update
        self.commit()
        return result

class FakeRepository(Repository):
    def __init__(self, batches: List[model.Batch], orders: List[model.Order]) -> None:
        self.batches = batches
        self.orders = orders
        self.committed = 0

    def add(self, batch:model.Batch):
        self.batches.append(batch)
    
    def get(self, class_object,class_object_column, reference) -> model.Batch:
        if class_object == model.Batch:
            queried_batch = next(batch_selected for batch_selected in self.batches if batch_selected.reference == reference)
        elif class_object == model.Order:
            queried_batch = next(batch_selected for batch_selected in self.orders if batch_selected.order_reference == reference)
        return queried_batch

    def list(self, class_object,class_object_column, filter):
        column_hash_map = {
            model.Batch.sku : "sku",
            model.Batch.reference : "reference",
        }
        col = column_hash_map.get(class_object_column)
        return [batch_selected for batch_selected in self.batches if getattr(batch_selected, col) == filter]

    def commit(self):
        self.committed = 1

    def rollback(self):
        pass

    def close(self):
        pass