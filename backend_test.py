import requests
import json
import time
from typing import Dict, List, Any, Optional

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://182f2e7f-cfb9-40a1-8cac-19063a8a3ed2.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "admin@shophub.com"
ADMIN_PASSWORD = "admin123"
CUSTOMER_EMAIL = "customer1@example.com"
CUSTOMER_PASSWORD = "customer123"

# Test data
TEST_USER = {
    "email": f"testuser_{int(time.time())}@example.com",
    "password": "testpassword123",
    "name": "Test User"
}

TEST_CATEGORY = {
    "name": f"Test Category {int(time.time())}",
    "description": "A test category for automated testing"
}

TEST_PRODUCT = {
    "name": f"Test Product {int(time.time())}",
    "description": "A test product for automated testing",
    "price": 19.99,
    "image_url": "https://via.placeholder.com/150",
    "stock": 50
}

TEST_ORDER = {
    "shipping_address": "123 Test Street, Test City, Test Country"
}

# Helper functions
def print_test_result(test_name: str, success: bool, details: str = ""):
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"{status} - {test_name}")
    if details:
        print(f"  Details: {details}")
    print()

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

def get_headers(token: str) -> Dict[str, str]:
    """Return headers with authorization token"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

# Test classes
class AuthenticationTests:
    @staticmethod
    def test_register():
        """Test user registration"""
        response = requests.post(
            f"{BACKEND_URL}/register",
            json=TEST_USER
        )
        
        success = response.status_code == 200
        details = ""
        
        if success:
            data = response.json()
            TEST_USER["id"] = data["user"]["id"]
            TEST_USER["token"] = data["token"]
            details = f"User registered with ID: {TEST_USER['id']}"
        else:
            details = f"Registration failed: {response.status_code} - {response.text}"
        
        print_test_result("User Registration", success, details)
        return success

    @staticmethod
    def test_login():
        """Test user login"""
        response = requests.post(
            f"{BACKEND_URL}/login",
            json={"email": TEST_USER["email"], "password": TEST_USER["password"]}
        )
        
        success = response.status_code == 200
        details = ""
        
        if success:
            data = response.json()
            TEST_USER["token"] = data["token"]
            details = "Login successful, token received"
        else:
            details = f"Login failed: {response.status_code} - {response.text}"
        
        print_test_result("User Login", success, details)
        return success

    @staticmethod
    def test_get_me():
        """Test getting current user profile"""
        if "token" not in TEST_USER:
            print_test_result("Get User Profile", False, "No token available, login first")
            return False
            
        response = requests.get(
            f"{BACKEND_URL}/me",
            headers=get_headers(TEST_USER["token"])
        )
        
        success = response.status_code == 200
        details = ""
        
        if success:
            data = response.json()
            details = f"Retrieved user profile: {data['name']} ({data['email']})"
        else:
            details = f"Get profile failed: {response.status_code} - {response.text}"
        
        print_test_result("Get User Profile", success, details)
        return success

class CategoryTests:
    category_id = None
    
    @staticmethod
    def test_create_category(admin_token: str):
        """Test category creation (admin only)"""
        response = requests.post(
            f"{BACKEND_URL}/categories",
            headers=get_headers(admin_token),
            json=TEST_CATEGORY
        )
        
        success = response.status_code == 200
        details = ""
        
        if success:
            data = response.json()
            CategoryTests.category_id = data["id"]
            details = f"Category created with ID: {CategoryTests.category_id}"
        else:
            details = f"Category creation failed: {response.status_code} - {response.text}"
        
        print_test_result("Create Category (Admin)", success, details)
        return success

    @staticmethod
    def test_get_categories():
        """Test getting all categories"""
        response = requests.get(f"{BACKEND_URL}/categories")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            categories = response.json()
            details = f"Retrieved {len(categories)} categories"
        else:
            details = f"Get categories failed: {response.status_code} - {response.text}"
        
        print_test_result("Get Categories", success, details)
        return success

    @staticmethod
    def test_delete_category(admin_token: str):
        """Test category deletion (admin only)"""
        if not CategoryTests.category_id:
            print_test_result("Delete Category (Admin)", False, "No category ID available")
            return False
            
        response = requests.delete(
            f"{BACKEND_URL}/categories/{CategoryTests.category_id}",
            headers=get_headers(admin_token)
        )
        
        success = response.status_code == 200
        details = ""
        
        if success:
            details = "Category deleted successfully"
        else:
            details = f"Category deletion failed: {response.status_code} - {response.text}"
        
        print_test_result("Delete Category (Admin)", success, details)
        return success

class ProductTests:
    product_id = None
    
    @staticmethod
    def test_create_product(admin_token: str, category_id: str):
        """Test product creation (admin only)"""
        product_data = TEST_PRODUCT.copy()
        product_data["category_id"] = category_id
        
        response = requests.post(
            f"{BACKEND_URL}/products",
            headers=get_headers(admin_token),
            json=product_data
        )
        
        success = response.status_code == 200
        details = ""
        
        if success:
            data = response.json()
            ProductTests.product_id = data["id"]
            details = f"Product created with ID: {ProductTests.product_id}"
        else:
            details = f"Product creation failed: {response.status_code} - {response.text}"
        
        print_test_result("Create Product (Admin)", success, details)
        return success

    @staticmethod
    def test_get_products():
        """Test getting all products"""
        response = requests.get(f"{BACKEND_URL}/products")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            products = response.json()
            details = f"Retrieved {len(products)} products"
        else:
            details = f"Get products failed: {response.status_code} - {response.text}"
        
        print_test_result("Get Products", success, details)
        return success

    @staticmethod
    def test_get_product_by_id():
        """Test getting a product by ID"""
        if not ProductTests.product_id:
            print_test_result("Get Product by ID", False, "No product ID available")
            return False
            
        response = requests.get(f"{BACKEND_URL}/products/{ProductTests.product_id}")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            product = response.json()
            details = f"Retrieved product: {product['name']}"
        else:
            details = f"Get product failed: {response.status_code} - {response.text}"
        
        print_test_result("Get Product by ID", success, details)
        return success

    @staticmethod
    def test_search_products():
        """Test searching products"""
        search_term = TEST_PRODUCT["name"][:10]  # Use part of the product name
        response = requests.get(f"{BACKEND_URL}/products?search={search_term}")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            products = response.json()
            details = f"Search returned {len(products)} products"
        else:
            details = f"Product search failed: {response.status_code} - {response.text}"
        
        print_test_result("Search Products", success, details)
        return success

    @staticmethod
    def test_filter_products_by_category(category_id: str):
        """Test filtering products by category"""
        response = requests.get(f"{BACKEND_URL}/products?category={category_id}")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            products = response.json()
            details = f"Filter returned {len(products)} products"
        else:
            details = f"Product filter failed: {response.status_code} - {response.text}"
        
        print_test_result("Filter Products by Category", success, details)
        return success

    @staticmethod
    def test_update_product(admin_token: str, category_id: str):
        """Test updating a product (admin only)"""
        if not ProductTests.product_id:
            print_test_result("Update Product (Admin)", False, "No product ID available")
            return False
            
        updated_product = TEST_PRODUCT.copy()
        updated_product["name"] = f"Updated {TEST_PRODUCT['name']}"
        updated_product["price"] = 29.99
        updated_product["category_id"] = category_id
        
        response = requests.put(
            f"{BACKEND_URL}/products/{ProductTests.product_id}",
            headers=get_headers(admin_token),
            json=updated_product
        )
        
        success = response.status_code == 200
        details = ""
        
        if success:
            product = response.json()
            details = f"Updated product: {product['name']} with price {product['price']}"
        else:
            details = f"Product update failed: {response.status_code} - {response.text}"
        
        print_test_result("Update Product (Admin)", success, details)
        return success

    @staticmethod
    def test_delete_product(admin_token: str):
        """Test deleting a product (admin only)"""
        if not ProductTests.product_id:
            print_test_result("Delete Product (Admin)", False, "No product ID available")
            return False
            
        response = requests.delete(
            f"{BACKEND_URL}/products/{ProductTests.product_id}",
            headers=get_headers(admin_token)
        )
        
        success = response.status_code == 200
        details = ""
        
        if success:
            details = "Product deleted successfully"
        else:
            details = f"Product deletion failed: {response.status_code} - {response.text}"
        
        print_test_result("Delete Product (Admin)", success, details)
        return success

class CartTests:
    @staticmethod
    def test_add_to_cart(token: str, product_id: str):
        """Test adding a product to cart"""
        response = requests.post(
            f"{BACKEND_URL}/cart",
            headers=get_headers(token),
            json={"product_id": product_id, "quantity": 2}
        )
        
        success = response.status_code == 200
        details = ""
        
        if success:
            details = "Product added to cart successfully"
        else:
            details = f"Add to cart failed: {response.status_code} - {response.text}"
        
        print_test_result("Add to Cart", success, details)
        return success

    @staticmethod
    def test_get_cart(token: str):
        """Test getting the user's cart"""
        response = requests.get(
            f"{BACKEND_URL}/cart",
            headers=get_headers(token)
        )
        
        success = response.status_code == 200
        details = ""
        
        if success:
            cart_items = response.json()
            details = f"Retrieved cart with {len(cart_items)} items"
        else:
            details = f"Get cart failed: {response.status_code} - {response.text}"
        
        print_test_result("Get Cart", success, details)
        return success, response.json() if success else []

    @staticmethod
    def test_update_cart_item(token: str, product_id: str):
        """Test updating cart item quantity"""
        response = requests.put(
            f"{BACKEND_URL}/cart/{product_id}?quantity=3",
            headers=get_headers(token)
        )
        
        success = response.status_code == 200
        details = ""
        
        if success:
            details = "Cart item quantity updated successfully"
        else:
            details = f"Update cart item failed: {response.status_code} - {response.text}"
        
        print_test_result("Update Cart Item", success, details)
        return success

    @staticmethod
    def test_remove_from_cart(token: str, product_id: str):
        """Test removing an item from cart"""
        response = requests.delete(
            f"{BACKEND_URL}/cart/{product_id}",
            headers=get_headers(token)
        )
        
        success = response.status_code == 200
        details = ""
        
        if success:
            details = "Item removed from cart successfully"
        else:
            details = f"Remove from cart failed: {response.status_code} - {response.text}"
        
        print_test_result("Remove from Cart", success, details)
        return success

class OrderTests:
    order_id = None
    
    @staticmethod
    def test_create_order(token: str, cart_items: List[Dict[str, Any]]):
        """Test creating an order from cart items"""
        if not cart_items:
            print_test_result("Create Order", False, "No cart items available")
            return False
            
        # Extract product_id and quantity from cart items
        items = [{"product_id": item["product_id"], "quantity": item["quantity"]} for item in cart_items]
        
        order_data = TEST_ORDER.copy()
        order_data["items"] = items
        
        response = requests.post(
            f"{BACKEND_URL}/orders",
            headers=get_headers(token),
            json=order_data
        )
        
        success = response.status_code == 200
        details = ""
        
        if success:
            order = response.json()
            OrderTests.order_id = order["id"]
            details = f"Order created with ID: {OrderTests.order_id}, total: ${order['total_amount']}"
        else:
            details = f"Order creation failed: {response.status_code} - {response.text}"
        
        print_test_result("Create Order", success, details)
        return success

    @staticmethod
    def test_get_user_orders(token: str):
        """Test getting user's order history"""
        response = requests.get(
            f"{BACKEND_URL}/orders",
            headers=get_headers(token)
        )
        
        success = response.status_code == 200
        details = ""
        
        if success:
            orders = response.json()
            details = f"Retrieved {len(orders)} orders"
        else:
            details = f"Get orders failed: {response.status_code} - {response.text}"
        
        print_test_result("Get User Orders", success, details)
        return success

    @staticmethod
    def test_get_all_orders(admin_token: str):
        """Test getting all orders (admin only)"""
        response = requests.get(
            f"{BACKEND_URL}/admin/orders",
            headers=get_headers(admin_token)
        )
        
        success = response.status_code == 200
        details = ""
        
        if success:
            orders = response.json()
            details = f"Retrieved {len(orders)} orders as admin"
        else:
            details = f"Get all orders failed: {response.status_code} - {response.text}"
        
        print_test_result("Get All Orders (Admin)", success, details)
        return success

    @staticmethod
    def test_update_order_status(admin_token: str, order_id: str):
        """Test updating order status (admin only)"""
        response = requests.put(
            f"{BACKEND_URL}/admin/orders/{order_id}?status=shipped",
            headers=get_headers(admin_token)
        )
        
        success = response.status_code == 200
        details = ""
        
        if success:
            order = response.json()
            details = f"Order status updated to: {order['status']}"
        else:
            details = f"Update order status failed: {response.status_code} - {response.text}"
        
        print_test_result("Update Order Status (Admin)", success, details)
        return success

class AdminTests:
    @staticmethod
    def test_get_admin_stats(admin_token: str):
        """Test getting admin dashboard statistics"""
        response = requests.get(
            f"{BACKEND_URL}/admin/stats",
            headers=get_headers(admin_token)
        )
        
        success = response.status_code == 200
        details = ""
        
        if success:
            stats = response.json()
            details = f"Stats: {stats['total_products']} products, {stats['total_orders']} orders, {stats['total_users']} users, ${stats['total_revenue']} revenue"
        else:
            details = f"Get admin stats failed: {response.status_code} - {response.text}"
        
        print_test_result("Get Admin Stats", success, details)
        return success

    @staticmethod
    def test_role_based_access(customer_token: str):
        """Test that customer cannot access admin routes"""
        # Try to access admin stats with customer token
        response = requests.get(
            f"{BACKEND_URL}/admin/stats",
            headers=get_headers(customer_token)
        )
        
        # Should fail with 403 Forbidden
        success = response.status_code == 403
        details = ""
        
        if success:
            details = "Customer correctly denied access to admin route"
        else:
            details = f"Role-based access control failed: {response.status_code} - {response.text}"
        
        print_test_result("Role-Based Access Control", success, details)
        return success

def run_all_tests():
    print("=" * 80)
    print("STARTING BACKEND API TESTS")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print("-" * 80)
    
    # Login as admin and customer
    print("Logging in as admin and customer...")
    admin_data = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    customer_data = login(CUSTOMER_EMAIL, CUSTOMER_PASSWORD)
    
    if not admin_data or not customer_data:
        print("❌ CRITICAL ERROR: Could not log in with test credentials")
        return
    
    admin_token = admin_data["token"]
    customer_token = customer_data["token"]
    
    print("-" * 80)
    print("1. AUTHENTICATION TESTS")
    print("-" * 80)
    auth_tests = AuthenticationTests()
    auth_tests.test_register()
    auth_tests.test_login()
    auth_tests.test_get_me()
    
    print("-" * 80)
    print("2. CATEGORY TESTS")
    print("-" * 80)
    category_tests = CategoryTests()
    category_tests.test_get_categories()
    
    # Get an existing category for product tests
    response = requests.get(f"{BACKEND_URL}/categories")
    if response.status_code == 200:
        categories = response.json()
        if categories:
            existing_category_id = categories[0]["id"]
        else:
            # Create a category if none exists
            category_tests.test_create_category(admin_token)
            existing_category_id = CategoryTests.category_id
    else:
        print("❌ CRITICAL ERROR: Could not get categories")
        return
    
    # Test category creation and deletion
    category_tests.test_create_category(admin_token)
    category_tests.test_delete_category(admin_token)
    
    print("-" * 80)
    print("3. PRODUCT TESTS")
    print("-" * 80)
    product_tests = ProductTests()
    product_tests.test_get_products()
    product_tests.test_create_product(admin_token, existing_category_id)
    product_tests.test_get_product_by_id()
    product_tests.test_search_products()
    product_tests.test_filter_products_by_category(existing_category_id)
    product_tests.test_update_product(admin_token, existing_category_id)
    
    # Save product ID for cart tests
    test_product_id = ProductTests.product_id
    
    # Get an existing product if test product creation failed
    if not test_product_id:
        response = requests.get(f"{BACKEND_URL}/products")
        if response.status_code == 200:
            products = response.json()
            if products:
                test_product_id = products[0]["id"]
            else:
                print("❌ CRITICAL ERROR: No products available for cart tests")
                return
    
    print("-" * 80)
    print("4. CART TESTS")
    print("-" * 80)
    cart_tests = CartTests()
    cart_tests.test_add_to_cart(customer_token, test_product_id)
    success, cart_items = cart_tests.test_get_cart(customer_token)
    cart_tests.test_update_cart_item(customer_token, test_product_id)
    
    print("-" * 80)
    print("5. ORDER TESTS")
    print("-" * 80)
    order_tests = OrderTests()
    
    # Add item to cart again if needed for order test
    if not cart_items:
        cart_tests.test_add_to_cart(customer_token, test_product_id)
        success, cart_items = cart_tests.test_get_cart(customer_token)
    
    if cart_items:
        order_tests.test_create_order(customer_token, cart_items)
        order_tests.test_get_user_orders(customer_token)
        order_tests.test_get_all_orders(admin_token)
        
        if OrderTests.order_id:
            order_tests.test_update_order_status(admin_token, OrderTests.order_id)
    
    print("-" * 80)
    print("6. ADMIN TESTS")
    print("-" * 80)
    admin_tests = AdminTests()
    admin_tests.test_get_admin_stats(admin_token)
    admin_tests.test_role_based_access(customer_token)
    
    # Clean up - delete test product
    if test_product_id == ProductTests.product_id:  # Only delete if it's our test product
        product_tests.test_delete_product(admin_token)
    
    print("=" * 80)
    print("BACKEND API TESTS COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    run_all_tests()