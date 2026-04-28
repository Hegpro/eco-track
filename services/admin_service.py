from db.mongo import db
import datetime

def add_area(name, pincode):
    area_id = name.lower().replace(" ", "_")
    area_data = {
        "area_id": area_id,
        "area_name": name,
        "pincode": pincode,
        "is_active": True
    }
    return db.db.areas.insert_one(area_data)

def add_topic(name, unit):
    topic_id = name.lower().replace(" ", "_")
    topic_data = {
        "topic_id": topic_id,
        "name": name,
        "unit": unit,
        "is_active": True
    }
    return db.db.topics.insert_one(topic_data)

def get_all_reports(limit=50):
    return list(db.reports.find().sort("timestamp", -1).limit(limit))

def get_users_in_area(area_id=None):
    query = {"area_id": area_id} if area_id else {}
    return list(db.users.find(query))
