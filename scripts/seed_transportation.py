#!/usr/bin/env python3

import sys
import os
import uuid
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append('/app/backend')

from pymongo import MongoClient

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URL)
db = client.ecommerce

# Collections
transportation_providers_collection = db.transportation_providers
vehicles_collection = db.vehicles

def seed_transportation_data():
    print("🚚 Seeding transportation management data...")
    
    # Clear existing transportation data
    print("🧹 Clearing existing transportation data...")
    transportation_providers_collection.delete_many({})
    vehicles_collection.delete_many({})
    
    # Create Transportation Providers
    print("📦 Creating transportation providers...")
    
    providers_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "SwiftDelivery Express",
            "service_type": "express",
            "base_cost": 80.0,
            "cost_per_km": 2.5,
            "estimated_days": 1,
            "service_areas": ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad"],
            "active": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Standard Logistics",
            "service_type": "standard",
            "base_cost": 40.0,
            "cost_per_km": 1.5,
            "estimated_days": 3,
            "service_areas": ["All India"],
            "active": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Premium Overnight",
            "service_type": "overnight",
            "base_cost": 150.0,
            "cost_per_km": 5.0,
            "estimated_days": 1,
            "service_areas": ["Major Cities"],
            "active": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "EconoShip",
            "service_type": "economy",
            "base_cost": 25.0,
            "cost_per_km": 1.0,
            "estimated_days": 5,
            "service_areas": ["All India"],
            "active": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "LocalDelivery Pro",
            "service_type": "local",
            "base_cost": 60.0,
            "cost_per_km": 3.0,
            "estimated_days": 1,
            "service_areas": ["Same City"],
            "active": True
        }
    ]
    
    transportation_providers_collection.insert_many(providers_data)
    print(f"✅ Created {len(providers_data)} transportation providers")
    
    # Create Vehicles
    print("🚛 Creating vehicles...")
    
    # Get provider IDs for vehicle assignment
    providers = list(transportation_providers_collection.find())
    
    vehicles_data = []
    vehicle_types = ["truck", "van", "bike"]
    locations = ["Delhi Hub", "Mumbai Hub", "Bangalore Hub", "Chennai Hub", "Kolkata Hub", "Hyderabad Hub"]
    
    for i, provider in enumerate(providers):
        for j in range(3):  # 3 vehicles per provider
            vehicle_id = str(uuid.uuid4())
            vehicle_type = vehicle_types[j % len(vehicle_types)]
            capacity = {"truck": 1000, "van": 500, "bike": 50}[vehicle_type]
            
            vehicle = {
                "id": vehicle_id,
                "provider_id": provider["id"],
                "vehicle_number": f"{provider['name'][:3].upper()}-{str(i+1).zfill(2)}{str(j+1).zfill(2)}",
                "driver_name": f"Driver {i+1}-{j+1}",
                "vehicle_type": vehicle_type,
                "capacity": capacity,
                "current_location": locations[j % len(locations)],
                "active": True
            }
            vehicles_data.append(vehicle)
    
    vehicles_collection.insert_many(vehicles_data)
    print(f"✅ Created {len(vehicles_data)} vehicles")
    
    print("🎉 Transportation management data seeded successfully!")
    print("\nTransportation Providers Summary:")
    for provider in providers_data:
        print(f"  • {provider['name']} ({provider['service_type']}) - ₹{provider['base_cost']} + ₹{provider['cost_per_km']}/km - {provider['estimated_days']} days")
    
    print(f"\nTotal Vehicles: {len(vehicles_data)}")
    for vehicle_type in vehicle_types:
        count = len([v for v in vehicles_data if v['vehicle_type'] == vehicle_type])
        print(f"  • {vehicle_type.title()}s: {count}")

if __name__ == "__main__":
    seed_transportation_data()