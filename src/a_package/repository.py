import abc
from a_package import model
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
        self.session.commit()
        return object

    def get(self, class_object,class_object_column,  reference):
        stmt = select(class_object).where(class_object_column == reference)
        result=self.session.execute(statement=stmt)
        return result.one