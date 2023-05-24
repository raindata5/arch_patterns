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
}

def handle(event: event, unit_of_work:uow.unit_of_work):
    result = []
    queue = [event]
    # with unit_of_work as uow:
    while len(queue) > 0:
        event_popped = queue.pop(0)
        for handler in messagebus[type(event)]:
            obj, repo, = handler(event, unit_of_work)
            # move from functional approach to OO contextmanager?
            queue.extend(repo.seen)
    return result.pop(0)

    #         obj_popped = uow.seen.pop()
    #             [
    #         handle(eve) for eve in obj_popped.events
    #         if eve
    #         ]