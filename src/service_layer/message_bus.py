from domain import (
    event,
    utils,
    command
)
from service_layer import services
from adapters import (
    uow
)
from typing import Union
# messagebus = {
#     event.BatchCreated: [services.add_batch],
#     event.BatchQuantityChanged:[services.modify_batch_quantity],
#     event.OutOfStockEvent: [services.null_handler],
# }

Message = Union[command.Command, event.Event]

EVENT_HANDLERS = {
    event.BatchCreated: [services.add_batch],
    event.BatchQuantityChanged:[services.modify_batch_quantity],
    event.OutOfStockEvent: [services.null_handler],
}
COMMAND_HANDLERS = {
    command.CreateBatch: [services.add_batch],
    command.Allocate: [services.allocate],
}
HANDLERS = {
    command.Command: COMMAND_HANDLERS,
    event.Event: EVENT_HANDLERS
}

def handle_event(event: event.Event, queue, unit_of_work:uow.unit_of_work):
    pass

def handle_command(command: command.Command, queue, unit_of_work:uow.unit_of_work):
    pass


def handle(message: Message, unit_of_work:uow.unit_of_work):
    results = []
    queue = [message]
    # with unit_of_work as uow:
    while len(queue) > 0:
        event_popped = queue.pop(0)
        struct_handler = HANDLERS[event_popped.__base__]
        if struct_handler == COMMAND_HANDLERS:
            pass
        elif struct_handler == EVENT_HANDLERS:
            pass
        for handler in struct_handler[type(event_popped)]:
            obj = handler(event_popped, unit_of_work)
            if obj:
                results.append(obj)
            queue.extend(unit_of_work.repo.collect_new_events())
    return results

    #         obj_popped = uow.seen.pop()
    #             [
    #         handle(eve) for eve in obj_popped.events
    #         if eve
    #         ]