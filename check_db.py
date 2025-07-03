from pymongo import MongoClient
import os

# Environment variables
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')

# MongoDB connection
client = MongoClient(MONGO_URL)
db = client.ecommerce

# Check users collection
print('Users in database:')
for user in db.users.find():
    print(f"- {user.get('email')} (role: {user.get('role')})")

print('\nTotal users:', db.users.count_documents({}))

# Check other collections
print('\nTotal products:', db.products.count_documents({}))
print('Total categories:', db.categories.count_documents({}))
print('Total orders:', db.orders.count_documents({}))