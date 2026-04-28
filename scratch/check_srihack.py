from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
db = client["srihack"]
print("Areas:", db.areas.count_documents({}))
print("Topics:", db.topics.count_documents({}))
print("Reports:", db.reports.count_documents({}))
print("Users:", db.users.count_documents({}))
