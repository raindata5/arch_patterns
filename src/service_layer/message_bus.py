from domain import (
    event,
    utils
)
from service_layer import services
from adapters import (
    uow
)

messagebus = {
    event.BatchCreated: [services.add_batch],
    event.AllocationRequired: [services.allocate],
    event.BatchQuantityChanged:[services.modify_batch_quantity],
    event.OutOfStockEvent: [services.null_handler],
}

def handle(event: event, unit_of_work:uow.unit_of_work):
    results = []
    queue = [event]
    # with unit_of_work as uow:
    while len(queue) > 0:
        event_popped = queue.pop(0)
        for handler in messagebus[type(event_popped)]:
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