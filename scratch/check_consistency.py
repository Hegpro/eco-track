from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
db = client["srihack"]
print("Sewage Reports:", db.reports.count_documents({"topic_id": "sewage_id"}))
print("Waste Reports:", db.reports.count_documents({"topic_id": "waste_id"}))
