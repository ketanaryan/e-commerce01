#!/usr/bin/env python3

import sys
import os
import uuid
import bcrypt
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append('/app/backend')

from pymongo import MongoClient

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URL)
db = client.ecommerce

# Collections
users_collection = db.users
products_collection = db.products
categories_collection = db.categories
orders_collection = db.orders
cart_collection = db.cart

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def seed_database():
    print("🌱 Seeding database...")
    
    # Clear existing data
    print("🧹 Clearing existing data...")
    users_collection.delete_many({})
    products_collection.delete_many({})
    categories_collection.delete_many({})
    orders_collection.delete_many({})
    cart_collection.delete_many({})
    
    # Create categories
    print("📂 Creating categories...")
    categories_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Electronics",
            "description": "Cameras, phones, laptops, and electronic gadgets"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Beauty & Health",
            "description": "Skincare, makeup, and health products"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Fashion",
            "description": "Clothing, accessories, and fashion items"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Home & Living",
            "description": "Furniture, decor, and home essentials"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Sports & Outdoors",
            "description": "Sports equipment, outdoor gear, and fitness products"
        }
    ]
    
    categories_collection.insert_many(categories_data)
    print(f"✅ Created {len(categories_data)} categories")
    
    # Create products using the images from vision expert
    print("📦 Creating products...")
    
    # Get category IDs for reference
    electronics_id = categories_data[0]["id"]
    beauty_id = categories_data[1]["id"]
    fashion_id = categories_data[2]["id"]
    home_id = categories_data[3]["id"]
    sports_id = categories_data[4]["id"]
    
    products_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Professional DSLR Camera",
            "description": "High-quality digital SLR camera perfect for photography enthusiasts and professionals. Features advanced autofocus and 4K video recording.",
            "price": 899.99,
            "image_url": "https://images.pexels.com/photos/90946/pexels-photo-90946.jpeg",
            "category_id": electronics_id,
            "category_name": "Electronics",
            "stock": 25
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Luxury Skincare Set",
            "description": "Premium skincare collection with moisturizer, serum, and cleanser. Perfect for daily skincare routine.",
            "price": 149.99,
            "image_url": "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwzfHxwcm9kdWN0c3xlbnwwfHx8fDE3NTE1MzgyODZ8MA&ixlib=rb-4.1.0&q=85",
            "category_id": beauty_id,
            "category_name": "Beauty & Health",
            "stock": 50
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Organic Beauty Products Bundle",
            "description": "Natural and organic beauty products including face masks, toners, and natural oils. Cruelty-free and eco-friendly.",
            "price": 89.99,
            "image_url": "https://images.unsplash.com/photo-1629198688000-71f23e745b6e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxfHxwcm9kdWN0c3xlbnwwfHx8fDE3NTE1MzgyODZ8MA&ixlib=rb-4.1.0&q=85",
            "category_id": beauty_id,
            "category_name": "Beauty & Health",
            "stock": 30
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Premium Shopping Bags Set",
            "description": "Eco-friendly reusable shopping bags made from sustainable materials. Perfect for grocery shopping and daily use.",
            "price": 24.99,
            "image_url": "https://images.unsplash.com/photo-1534452203293-494d7ddbf7e0?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwyfHxzaG9wcGluZ3xlbnwwfHx8fDE3NTE1MzgyOTB8MA&ixlib=rb-4.1.0&q=85",
            "category_id": fashion_id,
            "category_name": "Fashion",
            "stock": 100
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Wireless Bluetooth Headphones",
            "description": "Premium wireless headphones with noise cancellation and 30-hour battery life. Perfect for music lovers.",
            "price": 199.99,
            "image_url": "https://images.pexels.com/photos/2536965/pexels-photo-2536965.jpeg",
            "category_id": electronics_id,
            "category_name": "Electronics",
            "stock": 40
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Smart Home Security System",
            "description": "Complete home security system with cameras, sensors, and mobile app control. Keep your home safe 24/7.",
            "price": 299.99,
            "image_url": "https://images.unsplash.com/photo-1481437156560-3205f6a55735?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwzfHxzaG9wcGluZ3xlbnwwfHx8fDE3NTE1MzgyOTB8MA&ixlib=rb-4.1.0&q=85",
            "category_id": home_id,
            "category_name": "Home & Living",
            "stock": 15
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Laptop Computer - High Performance",
            "description": "Powerful laptop computer perfect for work, gaming, and creative projects. Features fast processor and ample storage.",
            "price": 1299.99,
            "image_url": "https://images.unsplash.com/photo-1599658880436-c61792e70672?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwyfHxlY29tbWVyY2V8ZW58MHx8fHwxNzUxNDUyMTgyfDA&ixlib=rb-4.1.0&q=85",
            "category_id": electronics_id,
            "category_name": "Electronics",
            "stock": 20
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Fitness Tracker Watch",
            "description": "Advanced fitness tracker with heart rate monitoring, GPS, and waterproof design. Track your health and fitness goals.",
            "price": 179.99,
            "image_url": "https://images.pexels.com/photos/50987/money-card-business-credit-card-50987.jpeg",
            "category_id": sports_id,
            "category_name": "Sports & Outdoors",
            "stock": 60
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Designer Sunglasses",
            "description": "Stylish designer sunglasses with UV protection and premium frames. Perfect for any occasion.",
            "price": 129.99,
            "image_url": "https://images.pexels.com/photos/2536965/pexels-photo-2536965.jpeg",
            "category_id": fashion_id,
            "category_name": "Fashion",
            "stock": 35
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Smart Kitchen Appliance Set",
            "description": "Modern kitchen appliances including smart blender, coffee maker, and food processor. Make cooking easier.",
            "price": 249.99,
            "image_url": "https://images.unsplash.com/photo-1481437156560-3205f6a55735?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwzfHxzaG9wcGluZ3xlbnwwfHx8fDE3NTE1MzgyOTB8MA&ixlib=rb-4.1.0&q=85",
            "category_id": home_id,
            "category_name": "Home & Living",
            "stock": 25
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Yoga Mat & Accessories",
            "description": "Premium yoga mat with carrying strap and blocks. Perfect for home workouts and yoga practice.",
            "price": 49.99,
            "image_url": "https://images.unsplash.com/photo-1534452203293-494d7ddbf7e0?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwyfHxzaG9wcGluZ3xlbnwwfHx8fDE3NTE1MzgyOTB8MA&ixlib=rb-4.1.0&q=85",
            "category_id": sports_id,
            "category_name": "Sports & Outdoors",
            "stock": 80
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Wireless Charging Station",
            "description": "Universal wireless charging station for phones, earbuds, and smartwatches. Charge multiple devices simultaneously.",
            "price": 79.99,
            "image_url": "https://images.pexels.com/photos/90946/pexels-photo-90946.jpeg",
            "category_id": electronics_id,
            "category_name": "Electronics",
            "stock": 45
        }
    ]
    
    products_collection.insert_many(products_data)
    print(f"✅ Created {len(products_data)} products")
    
    # Create users
    print("👥 Creating users...")
    
    # Create admin user
    admin_id = str(uuid.uuid4())
    admin_user = {
        "id": admin_id,
        "email": "admin@shophub.com",
        "name": "Admin User",
        "password": hash_password("admin123"),
        "role": "admin"
    }
    
    # Create regular customers
    customers_data = [
        {
            "id": str(uuid.uuid4()),
            "email": "customer1@example.com",
            "name": "John Doe",
            "password": hash_password("customer123"),
            "role": "customer"
        },
        {
            "id": str(uuid.uuid4()),
            "email": "customer2@example.com",
            "name": "Jane Smith",
            "password": hash_password("customer123"),
            "role": "customer"
        },
        {
            "id": str(uuid.uuid4()),
            "email": "customer3@example.com",
            "name": "Bob Johnson",
            "password": hash_password("customer123"),
            "role": "customer"
        }
    ]
    
    users_collection.insert_one(admin_user)
    users_collection.insert_many(customers_data)
    print(f"✅ Created 1 admin user and {len(customers_data)} customer users")
    
    # Create sample orders
    print("📋 Creating sample orders...")
    
    sample_orders = [
        {
            "id": str(uuid.uuid4()),
            "user_id": customers_data[0]["id"],
            "user_name": customers_data[0]["name"],
            "user_email": customers_data[0]["email"],
            "items": [
                {
                    "product_id": products_data[0]["id"],
                    "product_name": products_data[0]["name"],
                    "product_price": products_data[0]["price"],
                    "quantity": 1,
                    "total": products_data[0]["price"]
                },
                {
                    "product_id": products_data[1]["id"],
                    "product_name": products_data[1]["name"],
                    "product_price": products_data[1]["price"],
                    "quantity": 2,
                    "total": products_data[1]["price"] * 2
                }
            ],
            "total_amount": products_data[0]["price"] + (products_data[1]["price"] * 2),
            "status": "completed",
            "created_at": datetime.utcnow(),
            "shipping_address": "123 Main St, New York, NY 10001"
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": customers_data[1]["id"],
            "user_name": customers_data[1]["name"],
            "user_email": customers_data[1]["email"],
            "items": [
                {
                    "product_id": products_data[2]["id"],
                    "product_name": products_data[2]["name"],
                    "product_price": products_data[2]["price"],
                    "quantity": 1,
                    "total": products_data[2]["price"]
                }
            ],
            "total_amount": products_data[2]["price"],
            "status": "pending",
            "created_at": datetime.utcnow(),
            "shipping_address": "456 Oak Ave, Los Angeles, CA 90210"
        }
    ]
    
    orders_collection.insert_many(sample_orders)
    print(f"✅ Created {len(sample_orders)} sample orders")
    
    print("\n🎉 Database seeding completed successfully!")
    print("\n📊 Database Summary:")
    print(f"   Categories: {categories_collection.count_documents({})}")
    print(f"   Products: {products_collection.count_documents({})}")
    print(f"   Users: {users_collection.count_documents({})}")
    print(f"   Orders: {orders_collection.count_documents({})}")
    
    print("\n🔑 Login Credentials:")
    print("   Admin: admin@shophub.com / admin123")
    print("   Customer: customer1@example.com / customer123")
    print("   Customer: customer2@example.com / customer123")
    print("   Customer: customer3@example.com / customer123")

if __name__ == "__main__":
    seed_database()