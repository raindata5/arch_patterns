from domain import (
    event,
    utils
)

messagebus = {
    event.OutOfStockEvent: [utils.out_of_stock_handler]
}

def handle(event: event):
    for handler in messagebus[type(event)]:
        handler(event)