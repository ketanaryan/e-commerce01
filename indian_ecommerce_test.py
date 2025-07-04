import requests
import json
import time
from typing import Dict, List, Any, Optional

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://8322c09e-45ff-49e6-ae77-baef7fc3717c.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "admin@shophub.com"
ADMIN_PASSWORD = "admin123"
CUSTOMER1_EMAIL = "customer1@example.com"  # Arjun Sharma
CUSTOMER1_PASSWORD = "customer123"
CUSTOMER2_EMAIL = "customer2@example.com"  # Priya Patel
CUSTOMER2_PASSWORD = "customer123"

# Indian address for testing
INDIAN_ADDRESS = "42 Rajpath Avenue, New Delhi, Delhi 110001, India"

# Expected categories
EXPECTED_CATEGORIES = [
    "Mobiles & Electronics",
    "Fashion & Beauty",
    "Home & Kitchen",
    "Books & Education",
    "Sports & Fitness",
    "Groceries & Essentials"
]

# Expected products with INR pricing
EXPECTED_PRODUCTS = {
    "OPPO Reno 8 Pro": 45990,
    "Samsung Galaxy S22 Ultra": 124999,
}

# Helper functions
def get_headers(token: str) -> Dict[str, str]:
    """Return headers with authorization token"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def login(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Login and return the user data with token"""
    response = requests.post(
        f"{BACKEND_URL}/login",
        json={"email": email, "password": password}
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def run_indian_ecommerce_tests():
    print("=" * 80)
    print("STARTING INDIAN ECOMMERCE BACKEND API TESTS")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print("-" * 80)
    
    # 1. Test Authentication with Indian customer accounts
    print("-" * 80)
    print("1. AUTHENTICATION TESTS")
    print("-" * 80)
    
    # Login as admin and customers
    print("Logging in as admin and customers...")
    admin_data = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    customer1_data = login(CUSTOMER1_EMAIL, CUSTOMER1_PASSWORD)
    customer2_data = login(CUSTOMER2_EMAIL, CUSTOMER2_PASSWORD)
    
    if not admin_data or not customer1_data:
        print("❌ CRITICAL ERROR: Could not log in with test credentials")
        return
    
    admin_token = admin_data["token"]
    customer1_token = customer1_data["token"]
    customer2_token = customer2_data["token"] if customer2_data else None
    
    # Verify customer names
    print(f"Customer 1: {customer1_data['user']['name']} ({customer1_data['user']['email']})")
    if "Arjun Sharma" in customer1_data['user']['name']:
        print("✅ PASSED - Confirmed user is Arjun Sharma")
    else:
        print("❌ FAILED - Expected Arjun Sharma but got different name")
    
    if customer2_data:
        print(f"Customer 2: {customer2_data['user']['name']} ({customer2_data['user']['email']})")
        if "Priya Patel" in customer2_data['user']['name']:
            print("✅ PASSED - Confirmed user is Priya Patel")
        else:
            print("❌ FAILED - Expected Priya Patel but got different name")
    
    # 2. Test Categories (6 new Indian categories)
    print("-" * 80)
    print("2. CATEGORY TESTS")
    print("-" * 80)
    
    # Get categories
    response = requests.get(f"{BACKEND_URL}/categories")
    if response.status_code == 200:
        categories = response.json()
        print(f"Retrieved {len(categories)} categories")
        
        # Check if all expected categories exist
        category_names = [cat["name"] for cat in categories]
        print("Found categories:", ", ".join(category_names))
        
        missing_categories = [cat for cat in EXPECTED_CATEGORIES if cat not in category_names]
        if missing_categories:
            print(f"❌ FAILED - Missing expected categories: {', '.join(missing_categories)}")
        else:
            print(f"✅ PASSED - All expected categories found: {', '.join(EXPECTED_CATEGORIES)}")
    else:
        print(f"❌ FAILED - Get categories failed: {response.status_code} - {response.text}")
    
    # 3. Test Products (21 Indian products with INR pricing)
    print("-" * 80)
    print("3. PRODUCT TESTS")
    print("-" * 80)
    
    # Get products
    response = requests.get(f"{BACKEND_URL}/products")
    if response.status_code == 200:
        products = response.json()
        print(f"Retrieved {len(products)} products")
        
        # Check product count
        if len(products) < 21:
            print(f"❌ FAILED - Expected at least 21 products, but found only {len(products)}")
        else:
            print(f"✅ PASSED - Found at least 21 products as expected")
        
        # Check for INR pricing
        high_price_products = [p for p in products if p["price"] > 1000]
        print(f"Found {len(high_price_products)} products with high prices (>1000)")
        
        # Sample some products to display
        sample_products = products[:5]
        print("Sample products:")
        for product in sample_products:
            print(f"  - {product['name']}: ₹{product['price']:,}")
        
        # Check for specific products
        for expected_name, expected_price in EXPECTED_PRODUCTS.items():
            found = False
            for product in products:
                if expected_name in product["name"]:
                    found = True
                    print(f"Found product: {product['name']} - Price: ₹{product['price']:,}")
                    
                    # Check if price matches expected
                    if abs(product["price"] - expected_price) < 10:  # Allow small difference
                        print(f"✅ PASSED - Price matches expected: ₹{expected_price:,}")
                    else:
                        print(f"❌ FAILED - Price mismatch: Expected ₹{expected_price:,}, got ₹{product['price']:,}")
                    break
            
            if not found:
                print(f"❌ FAILED - Could not find product: {expected_name}")
    else:
        print(f"❌ FAILED - Get products failed: {response.status_code} - {response.text}")
        return
    
    # Get a product for cart tests
    test_product_id = products[0]["id"] if products else None
    
    if not test_product_id:
        print("❌ CRITICAL ERROR: No products available for cart tests")
        return
    
    # 4. Test Shopping Cart with Indian products
    print("-" * 80)
    print("4. CART TESTS")
    print("-" * 80)
    
    # Add product to cart
    response = requests.post(
        f"{BACKEND_URL}/cart",
        headers=get_headers(customer1_token),
        json={"product_id": test_product_id, "quantity": 2}
    )
    
    if response.status_code == 200:
        print("✅ PASSED - Product added to cart successfully")
    else:
        print(f"❌ FAILED - Add to cart failed: {response.status_code} - {response.text}")
    
    # Get cart
    response = requests.get(
        f"{BACKEND_URL}/cart",
        headers=get_headers(customer1_token)
    )
    
    cart_items = []
    if response.status_code == 200:
        cart_items = response.json()
        print(f"Retrieved cart with {len(cart_items)} items")
        
        if cart_items:
            # Show details of first item in cart
            first_item = cart_items[0]
            product = first_item.get("product", {})
            print(f"First item: {product.get('name', 'N/A')} - ₹{product.get('price', 0):,} x {first_item.get('quantity', 0)}")
            print("✅ PASSED - Cart retrieval successful")
        else:
            print("❌ FAILED - Cart is empty")
    else:
        print(f"❌ FAILED - Get cart failed: {response.status_code} - {response.text}")
    
    # 5. Test Order Management with Indian addresses
    print("-" * 80)
    print("5. ORDER TESTS")
    print("-" * 80)
    
    if cart_items:
        # Extract product_id and quantity from cart items
        items = [{"product_id": item["product_id"], "quantity": item["quantity"]} for item in cart_items]
        
        # Create order with Indian address
        order_data = {
            "items": items,
            "shipping_address": INDIAN_ADDRESS
        }
        
        response = requests.post(
            f"{BACKEND_URL}/orders",
            headers=get_headers(customer1_token),
            json=order_data
        )
        
        if response.status_code == 200:
            order = response.json()
            print(f"✅ PASSED - Order created with Indian address, total: ₹{order['total_amount']:,}")
            print(f"Shipping to: {order['shipping_address']}")
            
            # Verify the address is the Indian address we provided
            if INDIAN_ADDRESS not in order['shipping_address']:
                print(f"❌ FAILED - Expected Indian address not found in order")
            else:
                print(f"✅ PASSED - Indian address correctly saved in order")
        else:
            print(f"❌ FAILED - Order creation failed: {response.status_code} - {response.text}")
        
        # Get user orders
        response = requests.get(
            f"{BACKEND_URL}/orders",
            headers=get_headers(customer1_token)
        )
        
        if response.status_code == 200:
            orders = response.json()
            print(f"Retrieved {len(orders)} orders")
            
            if orders:
                # Show details of most recent order
                latest_order = orders[0]
                print(f"Latest order: ID {latest_order['id']}, Status: {latest_order['status']}")
                print(f"Total amount: ₹{latest_order['total_amount']:,}")
                print(f"Shipping to: {latest_order['shipping_address']}")
                
                # Check if any order has an Indian address
                indian_orders = [o for o in orders if "India" in o['shipping_address']]
                if indian_orders:
                    print(f"✅ PASSED - Found {len(indian_orders)} orders with Indian addresses")
                else:
                    print(f"❌ FAILED - No orders with Indian addresses found")
            
            print("✅ PASSED - Order history retrieval successful")
        else:
            print(f"❌ FAILED - Get orders failed: {response.status_code} - {response.text}")
    
    print("=" * 80)
    print("INDIAN ECOMMERCE BACKEND API TESTS COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    run_indian_ecommerce_tests()