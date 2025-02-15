import time

from app.helpers.tracer import (
    capture_lambda_handler,
    capture_method,
    trace_function,
    trace_segment,
)


@trace_function("validate_order")
def validate_order(order):
    time.sleep(1)  # Simulate processing time
    if not order.get("items"):
        raise ValueError("Order must contain at least one item")
    return True


@trace_function("process_payment")
def process_payment(order):
    time.sleep(2)  # Simulate processing time
    if order.get("payment_method") != "credit_card":
        raise ValueError("Unsupported payment method")
    return True


@trace_function("ship_order")
def ship_order(order):
    time.sleep(1.5)  # Simulate processing time
    return {"status": "shipped", "order_id": order.get("order_id")}


class OrderProcessor:
    @capture_method
    def process_order(self, order):
        validate_order(order)
        process_payment(order)
        return ship_order(order)


@capture_lambda_handler
def lambda_handler(event, context):
    order_processor = OrderProcessor()
    return order_processor.process_order(event)


def main(event, context):
    order = {
        "order_id": "12345",
        "items": ["item1", "item2"],
        "payment_method": "credit_card",
    }
    context = {}

    response = lambda_handler(order, context)

    with trace_segment(
        "additional_processing", {"order_id": order["order_id"]}
    ):
        time.sleep(1)  # Simulate additional processing time

    return response


if __name__ == "__main__":
    main()
