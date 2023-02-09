import abc
from domain import model
from sqlalchemy.orm import Session
from sqlalchemy import select

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

    def get(self, class_object,class_object_column, reference):
        stmt = select(class_object).where(class_object_column == reference)
        result=self.session.scalars(statement=stmt)
        return result.first()

    def list(self, class_object,class_object_column, filter):
        stmt = select(class_object).where(class_object_column == filter)
        result=self.session.scalars(statement=stmt)
        return result