from pymongo import MongoClient
import config

class Database:
    def __init__(self):
        # No certifi needed for typical local setup
        self.client = MongoClient(config.MONGO_URI)
        self.db = self.client[config.DB_NAME]
        
        # Collections
        self.users = self.db["users"]
        self.areas = self.db["areas"]
        self.topics = self.db["topics"]
        self.reports = self.db["reports"]
        self.nudges = self.db["nudges"]

    def get_user(self, user_id):
        return self.users.find_one({"user_id": user_id})

    def add_user(self, user_data):
        return self.users.insert_one(user_data)

    def update_user(self, user_id, update_data):
        return self.users.update_one({"user_id": user_id}, {"$set": update_data})

    def get_active_topics(self):
        return list(self.topics.find({"is_active": True}))

    def get_areas(self):
        return list(self.areas.find({"is_active": True}))

    def add_report(self, report_data):
        return self.reports.insert_one(report_data)

# Global database instance
db = Database()
