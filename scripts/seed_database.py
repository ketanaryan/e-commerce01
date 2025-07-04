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
transportation_providers_collection = db.transportation_providers
vehicles_collection = db.vehicles
shipments_collection = db.shipments
delivery_routes_collection = db.delivery_routes

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def seed_database():
    print("🌱 Seeding database with real Indian products...")
    
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
            "name": "Mobiles & Electronics",
            "description": "Smartphones, laptops, tablets, and electronic gadgets"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Fashion & Beauty",
            "description": "Clothing, accessories, skincare, and beauty products"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Home & Kitchen",
            "description": "Home appliances, furniture, decor, and kitchen essentials"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Books & Media",
            "description": "Books, movies, music, and educational content"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Sports & Fitness",
            "description": "Sports equipment, fitness gear, and outdoor activities"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Health & Personal Care",
            "description": "Health supplements, personal care, and wellness products"
        }
    ]
    
    categories_collection.insert_many(categories_data)
    print(f"✅ Created {len(categories_data)} categories")
    
    # Get category IDs for reference
    electronics_id = categories_data[0]["id"]
    fashion_id = categories_data[1]["id"]
    home_id = categories_data[2]["id"]
    books_id = categories_data[3]["id"]
    sports_id = categories_data[4]["id"]
    health_id = categories_data[5]["id"]
    
    # Create realistic Indian products with proper pricing in INR
    print("📦 Creating real Indian products...")
    
    products_data = [
        # Mobiles & Electronics
        {
            "id": str(uuid.uuid4()),
            "name": "OPPO Reno 8 Pro 5G (Glazed Green, 256GB)",
            "description": "50MP Portrait Camera, 80W SuperVOOC Charging, 6.7\" Curved AMOLED Display, Snapdragon 7 Gen 1, Android 12 based ColorOS 12.1",
            "price": 45990,
            "image_url": "https://images.unsplash.com/photo-1662371697742-b5b612c62629",
            "category_id": electronics_id,
            "category_name": "Mobiles & Electronics",
            "stock": 25
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Samsung Galaxy S23 Ultra 5G (Phantom Black, 256GB)",
            "description": "200MP Camera, S Pen, 6.8\" Dynamic AMOLED 2X Display, Snapdragon 8 Gen 2, 5000mAh Battery",
            "price": 124999,
            "image_url": "https://images.unsplash.com/photo-1662718870583-178b82eb74ca",
            "category_id": electronics_id,
            "category_name": "Mobiles & Electronics",
            "stock": 15
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Apple iPhone 14 Pro Max (Deep Purple, 128GB)",
            "description": "48MP Main Camera, A16 Bionic Chip, 6.7\" Super Retina XDR Display, Dynamic Island, iOS 16",
            "price": 139900,
            "image_url": "https://images.pexels.com/photos/5048613/pexels-photo-5048613.jpeg",
            "category_id": electronics_id,
            "category_name": "Mobiles & Electronics",
            "stock": 10
        },
        {
            "id": str(uuid.uuid4()),
            "name": "MacBook Air M2 Chip (Midnight, 8GB RAM, 256GB SSD)",
            "description": "13.6-inch Liquid Retina Display, M2 Chip with 8-core CPU and 8-core GPU, macOS Monterey, 18-hour battery life",
            "price": 114900,
            "image_url": "https://images.unsplash.com/photo-1498049794561-7780e7231661",
            "category_id": electronics_id,
            "category_name": "Mobiles & Electronics",
            "stock": 8
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Sony WH-1000XM4 Wireless Noise Canceling Headphones",
            "description": "Industry Leading Noise Cancelation, 30Hr Battery, Touch Sensor Controls, Speak-to-Chat Technology, Black",
            "price": 29990,
            "image_url": "https://images.unsplash.com/photo-1598965402089-897ce52e8355",
            "category_id": electronics_id,
            "category_name": "Mobiles & Electronics",
            "stock": 30
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Dell XPS 13 Laptop (Intel i7 12th Gen, 16GB RAM, 512GB SSD)",
            "description": "13.4\" FHD+ InfinityEdge Display, Intel Core i7-1250U, Windows 11 Home, Platinum Silver",
            "price": 134990,
            "image_url": "https://images.pexels.com/photos/356056/pexels-photo-356056.jpeg",
            "category_id": electronics_id,
            "category_name": "Mobiles & Electronics",
            "stock": 12
        },
        
        # Fashion & Beauty
        {
            "id": str(uuid.uuid4()),
            "name": "Fabindia Men's Cotton Straight Kurta (Navy Blue)",
            "description": "Pure Cotton, Regular Fit, Traditional Indian Wear, Perfect for Festivals and Casual Occasions",
            "price": 2490,
            "image_url": "https://images.unsplash.com/photo-1583391733956-6c78f0c9b7b2?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxfHxpbmRpYW4lMjBmYXNoaW9ufGVufDB8fHx8fDE3NTE1MzgyODZ8MA&ixlib=rb-4.1.0&q=85",
            "category_id": fashion_id,
            "category_name": "Fashion & Beauty",
            "stock": 50
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Lakme Absolute Perfect Radiance Skin Brightening Day Creme SPF 20",
            "description": "50g, With Vitamin E and Micro Crystals, Reduces Dark Spots, Brightens Skin Tone",
            "price": 1099,
            "image_url": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwyfHxiZWF1dHklMjBwcm9kdWN0c3xlbnwwfHx8fDE3NTE1MzgyODZ8MA&ixlib=rb-4.1.0&q=85",
            "category_id": fashion_id,
            "category_name": "Fashion & Beauty",
            "stock": 75
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Titan Raga Women's Analog Watch (Rose Gold)",
            "description": "Stainless Steel Case, Leather Strap, Water Resistant, 2-Year Warranty, Perfect for Gifting",
            "price": 8995,
            "image_url": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwzfHx3YXRjaHxlbnwwfHx8fDE3NTE1MzgyODZ8MA&ixlib=rb-4.1.0&q=85",
            "category_id": fashion_id,
            "category_name": "Fashion & Beauty",
            "stock": 40
        },
        
        # Home & Kitchen
        {
            "id": str(uuid.uuid4()),
            "name": "Prestige Induction Cooktop 2.0 (Black, 2000W)",
            "description": "Digital Display, 8 Preset Menus, Auto Switch Off, Overheat Protection, 2-Year Warranty",
            "price": 3499,
            "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHw0fHxraXRjaGVuJTIwYXBwbGlhbmNlc3xlbnwwfHx8fDE3NTE1MzgyODZ8MA&ixlib=rb-4.1.0&q=85",
            "category_id": home_id,
            "category_name": "Home & Kitchen",
            "stock": 35
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Godrej 190L 3 Star Direct-Cool Single Door Refrigerator",
            "description": "RD EDGE 205B 33 TAI, Aqua Blue, Base Stand Drawer, Toughened Glass Shelves",
            "price": 15990,
            "image_url": "https://images.unsplash.com/photo-1571175351734-79a99aeb43f5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHw1fHxyZWZyaWdlcmF0b3J8ZW58MHx8fHwxNzUxNTM4Mjg2fDA&ixlib=rb-4.1.0&q=85",
            "category_id": home_id,
            "category_name": "Home & Kitchen",
            "stock": 20
        },
        {
            "id": str(uuid.uuid4()),
            "name": "IKEA POÄNG Armchair (Birch veneer, Knisa light beige)",
            "description": "Comfortable Seating, Durable Construction, Modern Scandinavian Design, Easy to Assemble",
            "price": 12990,
            "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHw2fHxmdXJuaXR1cmV8ZW58MHx8fHwxNzUxNTM4Mjg2fDA&ixlib=rb-4.1.0&q=85",
            "category_id": home_id,
            "category_name": "Home & Kitchen",
            "stock": 15
        },
        
        # Books & Media
        {
            "id": str(uuid.uuid4()),
            "name": "The Alchemist by Paulo Coelho (Paperback)",
            "description": "International Bestseller, Inspirational Fiction, 163 Pages, Harper Collins Publishers",
            "price": 299,
            "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHw3fHxib29rc3xlbnwwfHx8fDE3NTE1MzgyODZ8MA&ixlib=rb-4.1.0&q=85",
            "category_id": books_id,
            "category_name": "Books & Media",
            "stock": 100
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Rich Dad Poor Dad by Robert Kiyosaki (English, Paperback)",
            "description": "Personal Finance, Investment Guide, 336 Pages, Plata Publishing, #1 Personal Finance Book",
            "price": 395,
            "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHw4fHxib29rc3xlbnwwfHx8fDE3NTE1MzgyODZ8MA&ixlib=rb-4.1.0&q=85",
            "category_id": books_id,
            "category_name": "Books & Media",
            "stock": 80
        },
        
        # Sports & Fitness
        {
            "id": str(uuid.uuid4()),
            "name": "Nivia Storm Football (Size 5, Multicolor)",
            "description": "FIFA Quality Pro, Hand Stitched, Rubber Bladder, Suitable for All Weather Conditions",
            "price": 1299,
            "image_url": "https://images.unsplash.com/photo-1614632537190-23e4b2e69946?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHw5fHxzcG9ydHN8ZW58MHx8fHwxNzUxNTM4Mjg2fDA&ixlib=rb-4.1.0&q=85",
            "category_id": sports_id,
            "category_name": "Sports & Fitness",
            "stock": 60
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Boldfit Gym Gloves for Weight Lifting (Black, Large)",
            "description": "Anti-Slip Palm, Breathable Material, Wrist Support, Perfect for Gym and Workout",
            "price": 799,
            "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxMHx8Zml0bmVzc3xlbnwwfHx8fDE3NTE1MzgyODZ8MA&ixlib=rb-4.1.0&q=85",
            "category_id": sports_id,
            "category_name": "Sports & Fitness",
            "stock": 45
        },
        
        # Health & Personal Care
        {
            "id": str(uuid.uuid4()),
            "name": "Himalaya Herbals Neem Face Wash (150ml)",
            "description": "Deep Cleansing, Removes Acne, Natural Ingredients, Suitable for Oily Skin, Dermatologically Tested",
            "price": 155,
            "image_url": "https://images.unsplash.com/photo-1556228578-8c89e6adf883?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxMXx8c2tpbmNhcmV8ZW58MHx8fHwxNzUxNTM4Mjg2fDA&ixlib=rb-4.1.0&q=85",
            "category_id": health_id,
            "category_name": "Health & Personal Care",
            "stock": 90
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Patanjali Coronil Kit (Coronil + Swasari + Anu Taila)",
            "description": "Ayurvedic Immunity Booster, Respiratory Health Support, 100% Natural, AYUSH Approved",
            "price": 545,
            "image_url": "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxMnx8YXl1cnZlZGljfGVufDB8fHx8fDE3NTE1MzgyODZ8MA&ixlib=rb-4.1.0&q=85",
            "category_id": health_id,
            "category_name": "Health & Personal Care",
            "stock": 70
        },
        
        # Additional trending products
        {
            "id": str(uuid.uuid4()),
            "name": "Fire-Boltt Phoenix Pro 1.39\" Bluetooth Calling Smartwatch",
            "description": "1.39\" HD Display, Bluetooth Calling, 120+ Sports Modes, SpO2 Monitoring, 7-Day Battery",
            "price": 4999,
            "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxM3x8c21hcnR3YXRjaHxlbnwwfHx8fDE3NTE1MzgyODZ8MA&ixlib=rb-4.1.0&q=85",
            "category_id": electronics_id,
            "category_name": "Mobiles & Electronics",
            "stock": 55
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bajaj Majesty RX11 1000-Watt Dry Iron (White and Blue)",
            "description": "Non-Stick Coated Sole Plate, Advanced Soleplate for Easy Gliding, ISI Approved, 2-Year Warranty",
            "price": 1299,
            "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxNHx8aXJvbnxlbnwwfHx8fDE3NTE1MzgyODZ8MA&ixlib=rb-4.1.0&q=85",
            "category_id": home_id,
            "category_name": "Home & Kitchen",
            "stock": 40
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Levi's Men's 511 Slim Jeans (Dark Blue, 32W x 34L)",
            "description": "Slim Fit, Comfort Stretch Denim, Classic 5-Pocket Styling, Perfect for Casual and Semi-Formal",
            "price": 3499,
            "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxNXx8amVhbnN8ZW58MHx8fHwxNzUxNTM4Mjg2fDA&ixlib=rb-4.1.0&q=85",
            "category_id": fashion_id,
            "category_name": "Fashion & Beauty",
            "stock": 65
        }
    ]
    
    products_collection.insert_many(products_data)
    print(f"✅ Created {len(products_data)} real Indian products")
    
    # Create users
    print("👥 Creating users...")
    
    # Create admin user
    admin_id = str(uuid.uuid4())
    admin_user = {
        "id": admin_id,
        "email": "admin@shophub.com",
        "name": "ShopHub Admin",
        "password": hash_password("admin123"),
        "role": "admin"
    }
    
    # Create regular customers with Indian names
    customers_data = [
        {
            "id": str(uuid.uuid4()),
            "email": "customer1@example.com",
            "name": "Arjun Sharma",
            "password": hash_password("customer123"),
            "role": "customer"
        },
        {
            "id": str(uuid.uuid4()),
            "email": "customer2@example.com",
            "name": "Priya Patel",
            "password": hash_password("customer123"),
            "role": "customer"
        },
        {
            "id": str(uuid.uuid4()),
            "email": "customer3@example.com",
            "name": "Rajesh Kumar",
            "password": hash_password("customer123"),
            "role": "customer"
        },
        {
            "id": str(uuid.uuid4()),
            "email": "customer4@example.com",
            "name": "Sneha Reddy",
            "password": hash_password("customer123"),
            "role": "customer"
        }
    ]
    
    users_collection.insert_one(admin_user)
    users_collection.insert_many(customers_data)
    print(f"✅ Created 1 admin user and {len(customers_data)} customer users")
    
    # Create sample orders with realistic Indian pricing
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
                    "product_id": products_data[4]["id"],
                    "product_name": products_data[4]["name"],
                    "product_price": products_data[4]["price"],
                    "quantity": 1,
                    "total": products_data[4]["price"]
                }
            ],
            "total_amount": products_data[0]["price"] + products_data[4]["price"],
            "status": "completed",
            "created_at": datetime.utcnow(),
            "shipping_address": "Flat 301, Sunrise Apartments, MG Road, Bangalore, Karnataka 560001"
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": customers_data[1]["id"],
            "user_name": customers_data[1]["name"],
            "user_email": customers_data[1]["email"],
            "items": [
                {
                    "product_id": products_data[1]["id"],
                    "product_name": products_data[1]["name"],
                    "product_price": products_data[1]["price"],
                    "quantity": 1,
                    "total": products_data[1]["price"]
                }
            ],
            "total_amount": products_data[1]["price"],
            "status": "pending",
            "created_at": datetime.utcnow(),
            "shipping_address": "B-42, Sector 15, Noida, Uttar Pradesh 201301"
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": customers_data[2]["id"],
            "user_name": customers_data[2]["name"],
            "user_email": customers_data[2]["email"],
            "items": [
                {
                    "product_id": products_data[6]["id"],
                    "product_name": products_data[6]["name"],
                    "product_price": products_data[6]["price"],
                    "quantity": 2,
                    "total": products_data[6]["price"] * 2
                },
                {
                    "product_id": products_data[12]["id"],
                    "product_name": products_data[12]["name"],
                    "product_price": products_data[12]["price"],
                    "quantity": 1,
                    "total": products_data[12]["price"]
                }
            ],
            "total_amount": (products_data[6]["price"] * 2) + products_data[12]["price"],
            "status": "completed",
            "created_at": datetime.utcnow(),
            "shipping_address": "12/A, Andheri West, Mumbai, Maharashtra 400058"
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
    print("   Customer: customer1@example.com / customer123 (Arjun Sharma)")
    print("   Customer: customer2@example.com / customer123 (Priya Patel)")
    print("   Customer: customer3@example.com / customer123 (Rajesh Kumar)")
    print("   Customer: customer4@example.com / customer123 (Sneha Reddy)")
    
    print("\n💰 Price Range:")
    print("   Electronics: ₹29,990 - ₹1,39,900")
    print("   Fashion: ₹1,099 - ₹8,995")
    print("   Home & Kitchen: ₹1,299 - ₹15,990")
    print("   Books: ₹299 - ₹395")
    print("   Sports: ₹799 - ₹1,299")
    print("   Health Care: ₹155 - ₹545")

if __name__ == "__main__":
    seed_database()