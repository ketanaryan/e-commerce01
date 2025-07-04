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

# Transportation Management Routes

# Transportation Providers
@app.get("/api/admin/transportation/providers")
async def get_transportation_providers(admin_id: str = Depends(get_admin_user)):
    providers = list(transportation_providers_collection.find())
    return [TransportationProvider(**provider) for provider in providers]

@app.post("/api/admin/transportation/providers")
async def create_transportation_provider(provider_data: TransportationProviderCreate, admin_id: str = Depends(get_admin_user)):
    provider_id = str(uuid.uuid4())
    provider = {
        "id": provider_id,
        "name": provider_data.name,
        "service_type": provider_data.service_type,
        "base_cost": provider_data.base_cost,
        "cost_per_km": provider_data.cost_per_km,
        "estimated_days": provider_data.estimated_days,
        "service_areas": provider_data.service_areas,
        "active": True
    }
    
    transportation_providers_collection.insert_one(provider)
    return TransportationProvider(**provider)

@app.put("/api/admin/transportation/providers/{provider_id}")
async def update_transportation_provider(provider_id: str, provider_data: TransportationProviderCreate, admin_id: str = Depends(get_admin_user)):
    update_data = {
        "name": provider_data.name,
        "service_type": provider_data.service_type,
        "base_cost": provider_data.base_cost,
        "cost_per_km": provider_data.cost_per_km,
        "estimated_days": provider_data.estimated_days,
        "service_areas": provider_data.service_areas
    }
    
    result = transportation_providers_collection.update_one({"id": provider_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Transportation provider not found")
    
    provider = transportation_providers_collection.find_one({"id": provider_id})
    return TransportationProvider(**provider)

@app.delete("/api/admin/transportation/providers/{provider_id}")
async def delete_transportation_provider(provider_id: str, admin_id: str = Depends(get_admin_user)):
    result = transportation_providers_collection.update_one(
        {"id": provider_id}, 
        {"$set": {"active": False}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Transportation provider not found")
    return {"message": "Transportation provider deactivated successfully"}

# Vehicles
@app.get("/api/admin/transportation/vehicles")
async def get_vehicles(admin_id: str = Depends(get_admin_user)):
    vehicles = list(vehicles_collection.find())
    return [Vehicle(**vehicle) for vehicle in vehicles]

@app.post("/api/admin/transportation/vehicles")
async def create_vehicle(vehicle_data: VehicleCreate, admin_id: str = Depends(get_admin_user)):
    # Verify provider exists
    provider = transportation_providers_collection.find_one({"id": vehicle_data.provider_id})
    if not provider:
        raise HTTPException(status_code=404, detail="Transportation provider not found")
    
    vehicle_id = str(uuid.uuid4())
    vehicle = {
        "id": vehicle_id,
        "provider_id": vehicle_data.provider_id,
        "vehicle_number": vehicle_data.vehicle_number,
        "driver_name": vehicle_data.driver_name,
        "vehicle_type": vehicle_data.vehicle_type,
        "capacity": vehicle_data.capacity,
        "current_location": vehicle_data.current_location,
        "active": True
    }
    
    vehicles_collection.insert_one(vehicle)
    return Vehicle(**vehicle)

@app.put("/api/admin/transportation/vehicles/{vehicle_id}")
async def update_vehicle(vehicle_id: str, vehicle_data: VehicleCreate, admin_id: str = Depends(get_admin_user)):
    update_data = {
        "provider_id": vehicle_data.provider_id,
        "vehicle_number": vehicle_data.vehicle_number,
        "driver_name": vehicle_data.driver_name,
        "vehicle_type": vehicle_data.vehicle_type,
        "capacity": vehicle_data.capacity,
        "current_location": vehicle_data.current_location
    }
    
    result = vehicles_collection.update_one({"id": vehicle_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    vehicle = vehicles_collection.find_one({"id": vehicle_id})
    return Vehicle(**vehicle)

@app.delete("/api/admin/transportation/vehicles/{vehicle_id}")
async def delete_vehicle(vehicle_id: str, admin_id: str = Depends(get_admin_user)):
    result = vehicles_collection.update_one(
        {"id": vehicle_id}, 
        {"$set": {"active": False}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"message": "Vehicle deactivated successfully"}

# Shipments
@app.get("/api/admin/transportation/shipments")
async def get_all_shipments(admin_id: str = Depends(get_admin_user)):
    shipments = list(shipments_collection.find().sort("created_at", -1))
    return [Shipment(**shipment) for shipment in shipments]

@app.get("/api/shipments/track/{tracking_number}")
async def track_shipment(tracking_number: str):
    shipment = shipments_collection.find_one({"tracking_number": tracking_number})
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    # Get additional info
    order = orders_collection.find_one({"id": shipment["order_id"]})
    provider = transportation_providers_collection.find_one({"id": shipment["provider_id"]})
    vehicle = vehicles_collection.find_one({"id": shipment["vehicle_id"]}) if shipment["vehicle_id"] else None
    
    result = Shipment(**shipment)
    
    return {
        "shipment": result,
        "order": Order(**order) if order else None,
        "provider": TransportationProvider(**provider) if provider else None,
        "vehicle": Vehicle(**vehicle) if vehicle else None
    }

@app.get("/api/orders/{order_id}/shipment")
async def get_order_shipment(order_id: str, user_id: str = Depends(get_current_user)):
    # Verify order belongs to user
    order = orders_collection.find_one({"id": order_id, "user_id": user_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    shipment = shipments_collection.find_one({"order_id": order_id})
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    # Get additional info
    provider = transportation_providers_collection.find_one({"id": shipment["provider_id"]})
    vehicle = vehicles_collection.find_one({"id": shipment["vehicle_id"]}) if shipment["vehicle_id"] else None
    
    result = Shipment(**shipment)
    
    return {
        "shipment": result,
        "provider": TransportationProvider(**provider) if provider else None,
        "vehicle": Vehicle(**vehicle) if vehicle else None
    }

@app.put("/api/admin/transportation/shipments/{shipment_id}")
async def update_shipment_status(shipment_id: str, shipment_update: ShipmentUpdate, admin_id: str = Depends(get_admin_user)):
    update_data = {
        "status": shipment_update.status,
        "delivery_notes": shipment_update.delivery_notes
    }
    
    # If status is delivered, set actual delivery time
    if shipment_update.status == "delivered":
        update_data["actual_delivery"] = datetime.utcnow()
        
        # Also update the order status
        shipment = shipments_collection.find_one({"id": shipment_id})
        if shipment:
            orders_collection.update_one(
                {"id": shipment["order_id"]},
                {"$set": {"status": "delivered"}}
            )
    
    result = shipments_collection.update_one({"id": shipment_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    shipment = shipments_collection.find_one({"id": shipment_id})
    return Shipment(**shipment)

# Delivery Routes
@app.get("/api/admin/transportation/routes")
async def get_delivery_routes(admin_id: str = Depends(get_admin_user)):
    routes = list(delivery_routes_collection.find().sort("date", -1))
    return [DeliveryRoute(**route) for route in routes]

@app.post("/api/admin/transportation/routes")
async def create_delivery_route(route_data: DeliveryRouteCreate, admin_id: str = Depends(get_admin_user)):
    # Verify vehicle exists
    vehicle = vehicles_collection.find_one({"id": route_data.vehicle_id})
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Verify all shipments exist and are available
    for shipment_id in route_data.shipments:
        shipment = shipments_collection.find_one({"id": shipment_id})
        if not shipment:
            raise HTTPException(status_code=404, detail=f"Shipment {shipment_id} not found")
        if shipment["status"] not in ["pending", "assigned"]:
            raise HTTPException(status_code=400, detail=f"Shipment {shipment_id} is not available for routing")
    
    route_id = str(uuid.uuid4())
    route = {
        "id": route_id,
        "vehicle_id": route_data.vehicle_id,
        "date": route_data.date,
        "shipments": route_data.shipments,
        "route_status": "planned",
        "total_distance": route_data.total_distance,
        "estimated_duration": route_data.estimated_duration,
        "created_at": datetime.utcnow()
    }
    
    delivery_routes_collection.insert_one(route)
    
    # Update shipments status to assigned
    shipments_collection.update_many(
        {"id": {"$in": route_data.shipments}},
        {"$set": {"status": "assigned", "vehicle_id": route_data.vehicle_id}}
    )
    
    return DeliveryRoute(**route)

@app.put("/api/admin/transportation/routes/{route_id}")
async def update_route_status(route_id: str, status: str, admin_id: str = Depends(get_admin_user)):
    valid_statuses = ["planned", "in_progress", "completed"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    result = delivery_routes_collection.update_one(
        {"id": route_id},
        {"$set": {"route_status": status}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Delivery route not found")
    
    # If route is in progress, update shipments to in_transit
    if status == "in_progress":
        route = delivery_routes_collection.find_one({"id": route_id})
        if route:
            shipments_collection.update_many(
                {"id": {"$in": route["shipments"]}},
                {"$set": {"status": "in_transit"}}
            )
    
    route = delivery_routes_collection.find_one({"id": route_id})
    return DeliveryRoute(**route)

# Calculate transportation cost for cart preview
@app.post("/api/cart/transportation-cost")
async def calculate_cart_transportation_cost(shipping_address: str, user_id: str = Depends(get_current_user)):
    # Get current cart items
    cart_items = list(cart_collection.find({"user_id": user_id}))
    
    if not cart_items:
        return {"cost": 0.0, "message": "Cart is empty"}
    
    # Convert cart items to order items format for calculation
    order_items = []
    for item in cart_items:
        product = products_collection.find_one({"id": item["product_id"]})
        if product:
            order_items.append({
                "product_id": item["product_id"],
                "quantity": item["quantity"],
                "price": product["price"]
            })
    
    transport_info = calculate_transportation_cost(shipping_address, order_items)
    
    return {
        "cost": transport_info["cost"],
        "provider_name": transport_info["provider_name"],
        "estimated_days": transport_info["estimated_days"],
        "distance": transport_info.get("distance", 0)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)