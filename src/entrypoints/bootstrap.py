from service_layer import message_bus
from adapters.orm import (
    engine,
    mapper_registry

) 
from sqlalchemy.orm import sessionmaker
from adapters import (
    uow
)
import adapters.repository as repository
import inspect
from functools import partial

def inject_dependencies(handler, dependencies: dict):
    sig = inspect.signature(handler)
    inject_deps = {
        dep_name: dep for dep_name, dep in dependencies.items()
        if sig.parameters.get(dep_name)
    }
    return partial(handler, **inject_deps) # handler(**inject_deps)

def bootstrap(
        create_from_metadata = True,
        uow = uow.unit_of_work(repository.SqlRepository(sessionmaker(bind=engine, expire_on_commit=False, autoflush=False,))),
        r = repository.RedisClient(sessionmaker(bind=engine, expire_on_commit=False, autoflush=False,))
):
    if create_from_metadata == True:
        mapper_registry.metadata.create_all(
            bind=(engine)
        )

    dependencies = {
        "uow": uow,
        "r": r
    }

    injected_event_handlers = {
        event_type: [inject_dependencies(eh, dependencies) for eh in event_handlers]
    for event_type, event_handlers in  message_bus.EVENT_HANDLERS
    }

    injected_command_handlers = {
        event_type: [inject_dependencies(eh, dependencies) for eh in event_handlers]
    for event_type, event_handlers in  message_bus.COMMAND_HANDLERS
    }

    

    return {
        'mb': message_bus.MessageBus(
            injected_event_handlers,
            injected_command_handlers,
            uow
        ),
        'r': r
    }
