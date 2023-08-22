import abc
from domain import (
    model,
    utils
)
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import (
    List,
    Union
)
import redis
import logging
import json
from dataclasses import asdict
from service_layer.message_bus import MessageBus
from domain import (
    event,
    command
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
        self.seen = []

    @utils.object_sensor
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
    
    def collect_new_events(self):
        for obj in self.seen:
            obj: model.Product
            while obj.events:
                yield obj.events.pop(0)

    def list(self, class_object,class_object_column, filter):

        stmt = select(class_object).where(class_object_column == filter)
        result=self.session.scalars(statement=stmt)
        # self.session.query().with_for_update
        self.commit()
        return result

class FakeRepository(Repository):
    def __init__(self, products: List[model.Product], orders: List[model.Order]) -> None:
        self.products = products
        self.orders = orders
        self.committed = 0
        self.seen = []

    @utils.object_sensor
    def add(self, product:model.Product):
        if product not in self.products:
            self.products.append(product)
        return product
    
    def get(self, class_object,class_object_column, reference) -> model.Batch:
        try:
            if class_object == model.Order:
                queried_obj = next(order_selected for order_selected in self.orders if order_selected.order_reference == reference)
            elif class_object == model.Product:
                queried_obj = next(product_selected for product_selected in self.products if product_selected.sku == reference)
        except StopIteration as ex:
            return None
        return queried_obj

    # def list(self, class_object,class_object_column, filter):
    #     column_hash_map = {
    #         model.Batch.sku : "sku",
    #         model.Batch.reference : "reference",
    #     }
    #     col = column_hash_map.get(class_object_column)
    #     return [batch_selected for batch_selected in self.batches if getattr(batch_selected, col) == filter]
    def collect_new_events(self):
        for obj in self.seen:
            obj: model.Product
            while obj.events:
                yield obj.events.pop(0)
    def commit(self):
        self.committed = 1

    def rollback(self):
        pass

    def close(self):
        pass

class RedisClient(Repository):
    CHANNELS = {
        'allocate': command.Allocate,
        'change_batch_quantity': command.ChangeBatchQuantity,
        'order_allocated': event.Allocated
    }
    def __init__(
        self,
        r: redis.Redis,
    ) -> None:
        self.r: redis.Redis = r
        # self.uow: unit_of_work = uow
        # self.message_bus: MessageBus = message_bus
        self.seen = []

    def add(self, channel, message):
        logging.info(f"publishing {message} to channel:{channel}")
        self.r.publish(channel=channel, message=json.dumps(asdict(message)))

    def get(self, message_bus):
        pubsub = self.r.pubsub(
            ignore_subscribe_messages=True
        )
        pubsub.subscribe(
            "change_batch_quantity",
            "allocate",
            "order_allocated"
        )
        for m in pubsub.listen():
            message_dict = m
            message_channel: bytes = message_dict["channel"]
            message_data: bytes = message_dict["data"]
            message_type = self.CHANNELS.get(message_channel.decode()) 
            message_obj_dict = json.loads(message_data)
            message_obj = message_type(**message_obj_dict)
            message_bus.handle(message_obj)
            # message_bus.handle(message_obj, unit_of_work=self.uow)