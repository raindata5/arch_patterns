import logging
from typing import (
    Union,
    Any
)

from adapters.orm import Session
import adapters.repository as repository
import domain.model as model
from service_layer.services import (
    allocate,
    InvalidOrderReference,
    InvalidSkuReference,
    add_batch,
    modify_batch_quantity
)
from domain.utils import (
    allocate_batch
)
import datetime as dt
from sqlalchemy import select
from adapters import (
    uow
)
from domain import (
    event,
    command
)
from service_layer import (
    views
)
from fastapi import (
    FastAPI,
    status,
    HTTPException,
    Request,
    Form
)
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from typing_extensions import Annotated
from entrypoints import bootstrap

logger = logging.getLogger()
logger.setLevel(logging.INFO)
# TODO: Does this use the same session repeatedly? Should be instantiated in endpoint?
sql_repo = repository.SqlRepository(Session())
app = FastAPI()

templates = Jinja2Templates(directory="src/templates")

bsed_deps = bootstrap.bootstrap()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return HTMLResponse(content = f'''<button> click me Mr.{request.headers.get('User-Agent')} </button>''', status_code=200)

@app.get("/batches/{batch_reference}", response_class=HTMLResponse)
def batches(request: Request, batch_reference: str):
    uow_tmp = bsed_deps["mb"].uow
    with uow_tmp as repo:
        logging.info(msg=f"{batch_reference}")
        print(batch_reference)
        queried_batch = repo.get(model.Batch, model.Batch.reference, batch_reference)
        sql_repo.commit()
    queried_batch: model.Batch
    return templates.TemplateResponse(
        "batch.html", {"batch_ref": queried_batch.reference, "request": request, "available_quantity": queried_batch.available_quantity}
    )

@app.get("/batch/{batch_reference}")
def read_batch(batch_reference: str):
    uow_tmp = uow.unit_of_work(sql_repo)
    with uow_tmp as repo:
        queried_batch = repo.get(model.Batch, model.Batch.reference, batch_reference)
        sql_repo.commit()
    return queried_batch

@app.post("/batches",  status_code=status.HTTP_201_CREATED,)
def add_batch_ep(batch_info: model.PreBatchInstance):
    cmd_new = command.CreateBatch(**batch_info.model_dump())
    inserted_batch = add_batch(command=cmd_new, unit_of_work=uow.unit_of_work(sql_repo))
    inserted_batch: model.Batch
    retrieved_batch = RedirectResponse(url=f"/batch/{inserted_batch.reference}", status_code=303)
    return retrieved_batch

@app.post("/allocate", status_code=status.HTTP_201_CREATED, )
def allocate_batch_ep(order_reference: model.OrderReference, sku: model.Sku):
    #TODO: Allow the client to specify a sku
    try:
        event_new = command.Allocate(**order_reference.model_dump(), **sku.model_dump())
        best_batch = allocate(event_new, uow.unit_of_work(sql_repo))
    except InvalidOrderReference as ex :
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=F"No order found with the following order_reference {order_reference}")
    except InvalidSkuReference as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=F"No batch found with the following {sku.sku}")
    except ValueError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=F"order:{ex.order_reference} not containing an order_line with the following sku: {sku.sku}")
    return best_batch

@app.get("/allocations/{order_reference}")
def read_order_allocations(order_reference: str) -> list:
    
    results = views.allocations(
        order_reference,
        unit_of_work=uow.unit_of_work(sql_repo)
    )
    return JSONResponse({"allocations": list(results)})

@app.get("/change_batch_quantity", response_class=HTMLResponse)
def change_batch_quantity(request: Request):
    return templates.TemplateResponse(
        "change_batch_quantity.html",
        {"request": request}
    )

@app.post("/change_batch_quantity", status_code=status.HTTP_201_CREATED,)
def change_batch_quantity(
    batch_reference: Annotated[str, Form(title="The reference number for the batch")],
    sku: Annotated[str, Form(title="The sku number for the batch")],
    new_quantity_offset: Annotated[int, Form(title="The offset for the batch available_quantity")]
):
    change_batch_quantity_form = {
        "batch_reference": batch_reference,
        "sku": sku,
        "new_quantity_offset": new_quantity_offset
    }
    comm = command.ChangeBatchQuantity(**change_batch_quantity_form)
    idx = modify_batch_quantity(command=comm, unit_of_work=uow.unit_of_work(sql_repo))
    retrieved_batch = RedirectResponse(url=f"/batches/{batch_reference}", status_code=303)
    return retrieved_batch



    # try:
    #     queried_order: Union[model.Order, Any] = sql_repo.get(model.Order, model.Order.order_reference, order_reference.order_reference)
    #     if not queried_order:
    #         raise HTTPException(status.HTTP_404_NOT_FOUND, detail=F"No order found with the following order_reference {order_reference}")
    #     logging.info(queried_order)
    #     queried_order_line = queried_order.search_order_line(sku.sku)
    #     sku_order_line = queried_order_line.sku
    #     logging.info(sku_order_line)
    #     queried_batches = sql_repo.list(model.Batch, model.Batch.sku, sku_order_line)
    #     queried_batches_list = list(queried_batches)
    #     if len(queried_batches_list) == 0:
    #         raise HTTPException(status.HTTP_404_NOT_FOUND, detail=F"No batch found with the following {sku_order_line}")
    #     logging.info(queried_batches_list) # run tests twice and print skus
    #     best_batch = allocate_batch(queried_order, queried_batches_list)
    # except HTTPException as ex:    
    #     raise
    # except ValueError as ex:
    #     raise HTTPException(status.HTTP_404_NOT_FOUND, detail=F"order:{queried_order.order_reference} not containing an order_line with the following sku: {sku.sku}")
    # finally:
    #     sql_repo.commit()
    # return best_batch

# from enum import IntEnum
# class ShippingState(IntEnum):
#     pass
# TODO: Refactor this descriptor that is far too specific (business logic contained)
