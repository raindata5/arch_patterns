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
    for handler in EVENT_HANDLERS[type(event)]:
        obj = handler(event, unit_of_work)
        queue.extend(unit_of_work.repo.collect_new_events())

    

def handle_command(command: command.Command, queue, unit_of_work:uow.unit_of_work):
    try:
        handler = COMMAND_HANDLERS[type(command)]
        obj = handler(command, unit_of_work) 
        queue.extend(unit_of_work.repo.collect_new_events())
    except Exception as ex:
        raise ex
    return obj


def handle(message: Message, unit_of_work:uow.unit_of_work):
    results = []
    queue = [message]
    # with unit_of_work as uow:
    while len(queue) > 0:
        message_popped = queue.pop(0)
        if isinstance(message_popped, command.Command):
            obj = handle_command(message_popped, queue, unit_of_work)
            if obj:
                results.append(obj)
        elif isinstance(message_popped, event.Event):
            handle_event(message_popped, queue, unit_of_work)
            # obj = handle_event(message_popped, queue, unit_of_work)
            # if obj:
            #     results.append(obj)

    return results

    #         obj_popped = uow.seen.pop()
    #             [
    #         handle(eve) for eve in obj_popped.events
    #         if eve
    #         ]