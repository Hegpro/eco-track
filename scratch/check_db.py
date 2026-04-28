import sys
import os
sys.path.append(os.getcwd())
from db.mongo import db

print("Areas:", list(db.db.areas.find({}, {"_id": 0})))
print("Topics:", list(db.db.topics.find({}, {"_id": 0})))
print("Reports:", db.reports.count_documents({}))
