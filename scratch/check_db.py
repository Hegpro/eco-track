from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client[os.getenv("DB_NAME", "srihack")]

print("--- AREAS ---")
for a in db.areas.find():
    print(a)

print("\n--- USERS (Sample) ---")
for u in db.users.find().limit(5):
    print(u)

print("\n--- REPORTS (Sample) ---")
for r in db.reports.find().limit(5):
    print(r)
