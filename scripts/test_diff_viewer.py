import json

from diffr import diff_hunks
from diffr.data_models.diff_model import Diff

if __name__ == "__main__":
    original = """def process_order(order_data):
    # Validate the order
    if not order_data.get('customer_id'):
        raise ValueError("Missing customer ID")
    if not order_data.get('items'):
        raise ValueError("No items in order")
    for item in order_data.get('items'):
        if not item.get('product_id'):
            raise ValueError("Item missing product ID")

    # Process the order
    total = sum(item.get('price', 0) for item in order_data.get('items'))
    order_id = generate_order_id()
    save_to_database(order_id, order_data, total)
    return order_id
"""
    updated = """def validate_order(order_data):
    if not order_data.get('customer_id'):
        raise ValueError("Missing customer ID")
    if not order_data.get('items'):
        raise ValueError("No items in order")
    for item in order_data.get('items'):
        if not item.get('product_id'):
            raise ValueError("Item missing product ID")

def process_order(order_data):
    # Validate the order
    validate_order(order_data)

    # Process the order
    total = sum(item.get('price', 0) for item in order_data.get('items'))
    order_id = generate_order_id()
    save_to_database(order_id, order_data, total)
    return order_id
"""
    output = diff_hunks(original, updated)
    print(json.dumps(output, indent=2))
    diff = Diff.from_hunks(output)
    print(diff)
