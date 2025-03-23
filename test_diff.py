# test_patience_diff.py
from diffr.algorithms.patience_cy import patience_diff


def run_test(test_id, original, updated):
    print(f"--- Test {test_id} ---")
    print("Original:")
    print(original)
    print("Updated:")
    print(updated)
    print("Diff Result:")
    result = patience_diff(original, updated)
    for line_pair in result:
        print(line_pair)
    print()

def main():
    # Test 1: Function signature change
    original = '''def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
    return total
'''
    updated = '''def calculate_total(items, tax_rate=0.1):
    total = 0
    for item in items:
        total += item.price
    total *= (1 + tax_rate)
    return total
'''
    run_test(1, original, updated)

    # Test 2: Adding a new method to a class
    original = '''class ShoppingCart:
    def __init__(self):
        self.items = []
        
    def add_item(self, item):
        self.items.append(item)
        
    def get_total(self):
        return sum(item.price for item in self.items)
'''
    updated = '''class ShoppingCart:
    def __init__(self):
        self.items = []
        
    def add_item(self, item):
        self.items.append(item)
        
    def remove_item(self, item_id):
        self.items = [item for item in self.items if item.id != item_id]
        
    def get_total(self):
        return sum(item.price for item in self.items)
'''
    run_test(2, original, updated)

    # Test 3: Refactoring - extract method
    original = '''def process_order(order_data):
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
'''
    updated = '''def validate_order(order_data):
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
'''
    run_test(3, original, updated)

    # Test 4: Bug fix - fixing a logical error
    original = '''def calculate_discount(subtotal, user_type):
    if user_type == "premium":
        if subtotal >= 100:
            return subtotal * 0.15
        else:
            return subtotal * 0.10
    elif user_type == "regular":
        return subtotal * 0.05
    else:
        return 0
'''
    updated = '''def calculate_discount(subtotal, user_type):
    if user_type == "premium":
        if subtotal >= 100:
            return subtotal * 0.15
        else:
            return subtotal * 0.10
    elif user_type == "regular":
        if subtotal >= 50:  # Bug fix: regular users should get discount only when subtotal >= 50
            return subtotal * 0.05
        else:
            return 0
    else:
        return 0
'''
    run_test(4, original, updated)
    
    # Test 5: Imports and docstring changes
    original = '''import os
import sys
from datetime import datetime

def log_error(error_msg):
    """Log error messages to the standard error stream."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sys.stderr.write(f"{timestamp} - ERROR: {error_msg}\\n")
'''
    updated = '''import os
import sys
import logging
from datetime import datetime

def log_error(error_msg, level='ERROR'):
    """
    Log error messages using the logging module.
    
    Args:
        error_msg: The error message to log
        level: The logging level (default: ERROR)
    """
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s')
    getattr(logging, level.lower())(error_msg)
'''
    run_test(5, original, updated)
    
    # Test 6: HTML code changes
    original = '''<!DOCTYPE html>
<html>
<head>
    <title>My Website</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>Welcome to My Website</h1>
        <nav>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/about">About</a></li>
                <li><a href="/contact">Contact</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <p>This is the main content.</p>
    </main>
    <footer>
        <p>&copy; 2023 My Website</p>
    </footer>
</body>
</html>
'''
    updated = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Website - Home</title>
    <link rel="stylesheet" href="styles.css">
    <script src="main.js" defer></script>
</head>
<body>
    <header>
        <h1>Welcome to My Website</h1>
        <nav>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/about">About</a></li>
                <li><a href="/contact">Contact</a></li>
                <li><a href="/blog">Blog</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <section class="hero">
            <h2>Welcome to our new website!</h2>
            <p>This is the main content with an updated design.</p>
            <button>Learn More</button>
        </section>
    </main>
    <footer>
        <p>&copy; 2023 My Website. All rights reserved.</p>
        <div class="social-links">
            <a href="#">Twitter</a>
            <a href="#">Facebook</a>
            <a href="#">Instagram</a>
        </div>
    </footer>
</body>
</html>
'''
    run_test(6, original, updated)
    
    # Test 7: JSON configuration changes
    original = '''{
  "name": "my-app",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.17.1",
    "mongoose": "^5.12.3",
    "react": "^17.0.2"
  },
  "scripts": {
    "start": "node server.js",
    "test": "jest"
  }
}
'''
    updated = '''{
  "name": "my-app",
  "version": "1.2.0",
  "dependencies": {
    "express": "^4.18.2",
    "mongoose": "^6.0.0",
    "react": "^18.2.0",
    "redux": "^4.2.1"
  },
  "devDependencies": {
    "jest": "^29.5.0",
    "eslint": "^8.40.0"
  },
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "test": "jest",
    "lint": "eslint ."
  }
}
'''
    run_test(7, original, updated)
    
    # Test 8: SQL query changes
    original = '''SELECT 
  customers.customer_id,
  customers.name,
  customers.email,
  orders.order_date,
  orders.total_amount
FROM 
  customers
JOIN 
  orders ON customers.customer_id = orders.customer_id
WHERE 
  orders.order_date >= '2023-01-01'
ORDER BY 
  orders.order_date DESC;
'''
    updated = '''SELECT 
  c.customer_id,
  c.name,
  c.email,
  o.order_date,
  o.total_amount,
  p.payment_method,
  p.payment_date
FROM 
  customers c
JOIN 
  orders o ON c.customer_id = o.customer_id
LEFT JOIN
  payments p ON o.order_id = p.order_id
WHERE 
  o.order_date >= '2023-01-01'
  AND o.status = 'completed'
GROUP BY
  c.customer_id, o.order_id, p.payment_id
ORDER BY 
  o.order_date DESC
LIMIT 100;
'''
    run_test(8, original, updated)

if __name__ == "__main__":
    main()
