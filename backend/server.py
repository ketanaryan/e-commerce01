from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List, Optional
import bcrypt
import jwt
import uuid
from datetime import datetime, timedelta
import os
from bson import ObjectId

# Environment variables
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
JWT_SECRET = os.environ.get('JWT_SECRET', 'fallback-secret-key')

# MongoDB connection
client = MongoClient(MONGO_URL)
db = client.ecommerce

# Collections
users_collection = db.users
products_collection = db.products
categories_collection = db.categories
orders_collection = db.orders
cart_collection = db.cart
transportation_providers_collection = db.transportation_providers
vehicles_collection = db.vehicles
shipments_collection = db.shipments
delivery_routes_collection = db.delivery_routes

# FastAPI app
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models
class User(BaseModel):
    id: str
    email: str
    name: str
    role: str = "customer"  # customer or admin

class UserRegister(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    image_url: str
    category_id: str
    category_name: str
    stock: int = 100

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    image_url: str
    category_id: str
    stock: int = 100

class Category(BaseModel):
    id: str
    name: str
    description: str

class CategoryCreate(BaseModel):
    name: str
    description: str

class CartItem(BaseModel):
    product_id: str
    quantity: int

class CartAdd(BaseModel):
    product_id: str
    quantity: int = 1

class Order(BaseModel):
    id: str
    user_id: str
    items: List[dict]
    total_amount: float
    transportation_cost: float = 0.0
    status: str
    created_at: datetime
    shipping_address: str
    user_name: str
    user_email: str

class OrderCreate(BaseModel):
    items: List[CartItem]
    shipping_address: str

# Transportation Management Models
class TransportationProvider(BaseModel):
    id: str
    name: str
    service_type: str  # "standard", "express", "overnight"
    base_cost: float
    cost_per_km: float
    estimated_days: int
    service_areas: List[str]
    active: bool = True

class TransportationProviderCreate(BaseModel):
    name: str
    service_type: str
    base_cost: float
    cost_per_km: float
    estimated_days: int
    service_areas: List[str]

class Vehicle(BaseModel):
    id: str
    provider_id: str
    vehicle_number: str
    driver_name: str
    vehicle_type: str  # "truck", "van", "bike"
    capacity: int
    current_location: str
    active: bool = True

class VehicleCreate(BaseModel):
    provider_id: str
    vehicle_number: str
    driver_name: str
    vehicle_type: str
    capacity: int
    current_location: str

class Shipment(BaseModel):
    id: str
    order_id: str
    provider_id: str
    vehicle_id: str
    tracking_number: str
    status: str  # "pending", "assigned", "picked_up", "in_transit", "out_for_delivery", "delivered", "returned"
    estimated_delivery: datetime
    actual_delivery: Optional[datetime] = None
    delivery_notes: str = ""
    created_at: datetime

class ShipmentCreate(BaseModel):
    order_id: str
    provider_id: str

class ShipmentUpdate(BaseModel):
    status: str
    delivery_notes: str = ""

class DeliveryRoute(BaseModel):
    id: str
    vehicle_id: str
    date: datetime
    shipments: List[str]  # shipment IDs
    route_status: str  # "planned", "in_progress", "completed"
    total_distance: float
    estimated_duration: int  # minutes
    created_at: datetime

class DeliveryRouteCreate(BaseModel):
    vehicle_id: str
    date: datetime
    shipments: List[str]
    total_distance: float
    estimated_duration: int

# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    return verify_token(credentials.credentials)

def get_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    user_id = verify_token(credentials.credentials)
    user = users_collection.find_one({"id": user_id})
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user_id

# Transportation helper functions
def calculate_transportation_cost(shipping_address: str, items: List[dict]) -> dict:
    """Calculate transportation cost based on distance and weight"""
    import random
    
    # Simulate distance calculation (in real scenario, use address parsing)
    estimated_distance = random.randint(5, 50)  # 5-50 km
    
    # Calculate total weight (simulate based on item count)
    total_weight = sum(item.get('quantity', 1) for item in items)
    
    # Get available providers
    providers = list(transportation_providers_collection.find({"active": True}))
    
    if not providers:
        return {
            "provider_id": None,
            "cost": 50.0,  # Default cost
            "estimated_days": 3,
            "provider_name": "Standard Delivery"
        }
    
    # Select cheapest provider for the distance
    best_provider = min(providers, key=lambda p: p["base_cost"] + (p["cost_per_km"] * estimated_distance))
    
    cost = best_provider["base_cost"] + (best_provider["cost_per_km"] * estimated_distance)
    
    # Add weight factor
    if total_weight > 5:
        cost += (total_weight - 5) * 10  # Additional cost for heavy items
    
    return {
        "provider_id": best_provider["id"],
        "cost": round(cost, 2),
        "estimated_days": best_provider["estimated_days"],
        "provider_name": best_provider["name"],
        "distance": estimated_distance
    }

def generate_tracking_number() -> str:
    """Generate a unique tracking number"""
    import random
    import string
    prefix = "TRK"
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{prefix}{suffix}"

def create_shipment_for_order(order_id: str, provider_id: str) -> str:
    """Create a shipment for an order"""
    shipment_id = str(uuid.uuid4())
    tracking_number = generate_tracking_number()
    
    # Find available vehicle from the provider
    vehicle = vehicles_collection.find_one({"provider_id": provider_id, "active": True})
    vehicle_id = vehicle["id"] if vehicle else None
    
    # Calculate estimated delivery (add provider's estimated days)
    provider = transportation_providers_collection.find_one({"id": provider_id})
    estimated_days = provider["estimated_days"] if provider else 3
    estimated_delivery = datetime.utcnow() + timedelta(days=estimated_days)
    
    shipment = {
        "id": shipment_id,
        "order_id": order_id,
        "provider_id": provider_id,
        "vehicle_id": vehicle_id,
        "tracking_number": tracking_number,
        "status": "pending",
        "estimated_delivery": estimated_delivery,
        "actual_delivery": None,
        "delivery_notes": "",
        "created_at": datetime.utcnow()
    }
    
    shipments_collection.insert_one(shipment)
    return shipment_id

# Routes

# Auth routes
@app.post("/api/register")
async def register(user_data: UserRegister):
    if users_collection.find_one({"email": user_data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user_data.password)
    
    user = {
        "id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "password": hashed_password,
        "role": "customer"
    }
    
    users_collection.insert_one(user)
    token = create_token(user_id)
    
    return {"token": token, "user": User(**user)}

@app.post("/api/login")
async def login(user_data: UserLogin):
    user = users_collection.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user["id"])
    return {"token": token, "user": User(**user)}

@app.get("/api/me")
async def get_me(user_id: str = Depends(get_current_user)):
    user = users_collection.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

# Product routes
@app.get("/api/products")
async def get_products(search: Optional[str] = None, category: Optional[str] = None):
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    if category:
        query["category_id"] = category
    
    products = list(products_collection.find(query))
    return [Product(**product) for product in products]

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    product = products_collection.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**product)

@app.post("/api/products")
async def create_product(product_data: ProductCreate, admin_id: str = Depends(get_admin_user)):
    category = categories_collection.find_one({"id": product_data.category_id})
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")
    
    product_id = str(uuid.uuid4())
    product = {
        "id": product_id,
        "name": product_data.name,
        "description": product_data.description,
        "price": product_data.price,
        "image_url": product_data.image_url,
        "category_id": product_data.category_id,
        "category_name": category["name"],
        "stock": product_data.stock
    }
    
    products_collection.insert_one(product)
    return Product(**product)

@app.put("/api/products/{product_id}")
async def update_product(product_id: str, product_data: ProductCreate, admin_id: str = Depends(get_admin_user)):
    category = categories_collection.find_one({"id": product_data.category_id})
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")
    
    update_data = {
        "name": product_data.name,
        "description": product_data.description,
        "price": product_data.price,
        "image_url": product_data.image_url,
        "category_id": product_data.category_id,
        "category_name": category["name"],
        "stock": product_data.stock
    }
    
    result = products_collection.update_one({"id": product_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = products_collection.find_one({"id": product_id})
    return Product(**product)

@app.delete("/api/products/{product_id}")
async def delete_product(product_id: str, admin_id: str = Depends(get_admin_user)):
    result = products_collection.delete_one({"id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

# Category routes
@app.get("/api/categories")
async def get_categories():
    categories = list(categories_collection.find())
    return [Category(**category) for category in categories]

@app.post("/api/categories")
async def create_category(category_data: CategoryCreate, admin_id: str = Depends(get_admin_user)):
    category_id = str(uuid.uuid4())
    category = {
        "id": category_id,
        "name": category_data.name,
        "description": category_data.description
    }
    
    categories_collection.insert_one(category)
    return Category(**category)

@app.delete("/api/categories/{category_id}")
async def delete_category(category_id: str, admin_id: str = Depends(get_admin_user)):
    result = categories_collection.delete_one({"id": category_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}

# Cart routes
@app.get("/api/cart")
async def get_cart(user_id: str = Depends(get_current_user)):
    cart_items = list(cart_collection.find({"user_id": user_id}))
    
    # Get product details for each cart item
    cart_with_products = []
    for item in cart_items:
        product = products_collection.find_one({"id": item["product_id"]})
        if product:
            cart_with_products.append({
                "product_id": item["product_id"],
                "quantity": item["quantity"],
                "product": Product(**product)
            })
    
    return cart_with_products

@app.post("/api/cart")
async def add_to_cart(item: CartAdd, user_id: str = Depends(get_current_user)):
    product = products_collection.find_one({"id": item.product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    existing_item = cart_collection.find_one({"user_id": user_id, "product_id": item.product_id})
    
    if existing_item:
        cart_collection.update_one(
            {"user_id": user_id, "product_id": item.product_id},
            {"$inc": {"quantity": item.quantity}}
        )
    else:
        cart_collection.insert_one({
            "user_id": user_id,
            "product_id": item.product_id,
            "quantity": item.quantity
        })
    
    return {"message": "Item added to cart"}

@app.put("/api/cart/{product_id}")
async def update_cart_item(product_id: str, quantity: int, user_id: str = Depends(get_current_user)):
    if quantity <= 0:
        cart_collection.delete_one({"user_id": user_id, "product_id": product_id})
    else:
        cart_collection.update_one(
            {"user_id": user_id, "product_id": product_id},
            {"$set": {"quantity": quantity}}
        )
    
    return {"message": "Cart updated"}

@app.delete("/api/cart/{product_id}")
async def remove_from_cart(product_id: str, user_id: str = Depends(get_current_user)):
    cart_collection.delete_one({"user_id": user_id, "product_id": product_id})
    return {"message": "Item removed from cart"}

# Order routes
@app.post("/api/orders")
async def create_order(order_data: OrderCreate, user_id: str = Depends(get_current_user)):
    user = users_collection.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate total and prepare order items
    order_items = []
    subtotal = 0
    
    for item in order_data.items:
        product = products_collection.find_one({"id": item.product_id})
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        item_total = product["price"] * item.quantity
        subtotal += item_total
        
        order_items.append({
            "product_id": item.product_id,
            "product_name": product["name"],
            "product_price": product["price"],
            "quantity": item.quantity,
            "total": item_total
        })
    
    # Calculate transportation cost
    transport_info = calculate_transportation_cost(order_data.shipping_address, order_items)
    transportation_cost = transport_info["cost"]
    total_amount = subtotal + transportation_cost
    
    order_id = str(uuid.uuid4())
    order = {
        "id": order_id,
        "user_id": user_id,
        "user_name": user["name"],
        "user_email": user["email"],
        "items": order_items,
        "total_amount": total_amount,
        "transportation_cost": transportation_cost,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "shipping_address": order_data.shipping_address
    }
    
    orders_collection.insert_one(order)
    
    # Create shipment if provider is available
    if transport_info["provider_id"]:
        shipment_id = create_shipment_for_order(order_id, transport_info["provider_id"])
        # Update order status to show it's been assigned for shipping
        orders_collection.update_one(
            {"id": order_id},
            {"$set": {"status": "confirmed"}}
        )
        order["status"] = "confirmed"
    
    # Clear cart
    cart_collection.delete_many({"user_id": user_id})
    
    return Order(**order)

@app.get("/api/orders")
async def get_orders(user_id: str = Depends(get_current_user)):
    orders = list(orders_collection.find({"user_id": user_id}).sort("created_at", -1))
    return [Order(**order) for order in orders]

@app.get("/api/admin/orders")
async def get_all_orders(admin_id: str = Depends(get_admin_user)):
    orders = list(orders_collection.find().sort("created_at", -1))
    return [Order(**order) for order in orders]

@app.put("/api/admin/orders/{order_id}")
async def update_order_status(order_id: str, status: str, admin_id: str = Depends(get_admin_user)):
    result = orders_collection.update_one(
        {"id": order_id},
        {"$set": {"status": status}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_collection.find_one({"id": order_id})
    return Order(**order)

@app.get("/api/admin/stats")
async def get_admin_stats(admin_id: str = Depends(get_admin_user)):
    total_products = products_collection.count_documents({})
    total_orders = orders_collection.count_documents({})
    total_users = users_collection.count_documents({"role": "customer"})
    
    # Calculate total revenue
    orders = list(orders_collection.find({"status": {"$in": ["completed", "pending"]}}))
    total_revenue = sum(order["total_amount"] for order in orders)
    
    return {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_users": total_users,
        "total_revenue": total_revenue
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)