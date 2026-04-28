from db.mongo import db
from services import admin_service
import datetime

def seed():
    print("Seeding local database 'srihack'...")
    
    # 1. Add Areas
    areas = [
        ("Indiranagar", "560038"),
        ("Koramangala", "560034"),
        ("Whitefield", "560066")
    ]
    for name, pincode in areas:
        if not db.db.areas.find_one({"area_name": name}):
            admin_service.add_area(name, pincode)
            print(f"Added area: {name}")
        else:
            print(f"Area {name} already exists.")
            
    # 2. Add Topics
    topics = [
        ("Water Usage", "Litres"),
        ("Electricity", "kWh"),
        ("Waste Produced", "kg")
    ]
    for name, unit in topics:
        if not db.db.topics.find_one({"name": name}):
            admin_service.add_topic(name, unit)
            print(f"Added topic: {name}")
        else:
            print(f"Topic {name} already exists.")
            
    # 3. Add Sample Users
    sample_users = [
        {
            "user_id": 12345678,
            "name": "Test User 1",
            "area_id": "indiranagar",
            "area_name": "Indiranagar",
            "pincode": "560038",
            "registered_at": datetime.datetime.now()
        }
    ]
    for user_data in sample_users:
        if not db.db.users.find_one({"user_id": user_data["user_id"]}):
            db.add_user(user_data)
            print(f"Added user: {user_data['name']}")
        else:
            print(f"User {user_data['name']} already exists.")
            
    print("Seeding complete.")

if __name__ == "__main__":
    seed()
