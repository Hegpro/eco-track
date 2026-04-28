from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
db = client["srihack"]
report = db.reports.find_one()
print(report)
