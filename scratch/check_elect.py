from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
db = client["srihack"]
print(db.reports.find_one({"topic_id": {"$regex": "elect"}}))
