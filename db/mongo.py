from pymongo import MongoClient
import config
from utils.errors import DatabaseError
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        try:
            self.client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
            self.db = self.client[config.DB_NAME]
            # Collections
            self.users = self.db["users"]
            self.areas = self.db["areas"]
            self.topics = self.db["topics"]
            self.reports = self.db["reports"]
            self.nudges = self.db["nudges"]
            self.staff = self.db["staff"]
            self.scores = self.db["scores"]
            
            # Check connection
            self.client.server_info()
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise DatabaseError(f"Database connection failed: {e}")

    def safe_execute(func):
        """Decorator to wrap database operations with error handling"""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Database operation failed in {func.__name__}: {e}")
                raise DatabaseError(f"Operation failed: {e}")
        return wrapper

    @safe_execute
    def get_user(self, user_id):
        return self.users.find_one({"user_id": user_id})

    @safe_execute
    def add_user(self, user_data):
        return self.users.insert_one(user_data)

    @safe_execute
    def update_user(self, user_id, update_data):
        return self.users.update_one({"user_id": user_id}, {"$set": update_data})

    @safe_execute
    def get_active_topics(self):
        return list(self.topics.find({"is_active": True}))

    @safe_execute
    def get_areas(self):
        return list(self.areas.find({"is_active": True}))

    @safe_execute
    def add_report(self, report_data):
        return self.reports.insert_one(report_data)

    @safe_execute
    def get_open_reports(self, area_id):
        return list(self.reports.find({"area_id": area_id, "status": "Open"}))

    @safe_execute
    def add_staff(self, staff_data):
        return self.staff.update_one(
            {"user_id": staff_data["user_id"]},
            {"$set": staff_data},
            upsert=True
        )

    @safe_execute
    def is_staff(self, user_id):
        return self.staff.find_one({"user_id": user_id})

    @safe_execute
    def get_dept_reports(self, dept_id, status="Open"):
        return list(self.reports.find({"topic_id": dept_id, "status": status}))

    @safe_execute
    def resolve_report(self, report_id, staff_id):
        from bson import ObjectId
        import datetime
        return self.reports.update_one(
            {"_id": ObjectId(report_id)},
            {"$set": {
                "status": "Resolved",
                "resolved_at": datetime.datetime.now(),
                "resolved_by": staff_id
            }}
        )

    @safe_execute
    def get_area_score(self, area_id):
        area = self.areas.find_one({"area_id": area_id})
        return area.get("current_score", 100) if area else 100

    @safe_execute
    def update_area_score(self, area_id, score_delta):
        return self.areas.update_one(
            {"area_id": area_id},
            {"$inc": {"current_score": score_delta}, "$setOnInsert": {"current_score": 100}},
            upsert=True
        )

# Global database instance
try:
    db = Database()
except DatabaseError:
    # Allow import but database operations will fail gracefully later
    db = None
    logger.warning("Database initialized in disconnected state.")
