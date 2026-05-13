from pymongo import MongoClient
import config
from utils.errors import DatabaseError
import logging
import certifi

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        try:
            # Mask URI for logging
            masked_uri = config.MONGO_URI.split('@')[-1] if '@' in config.MONGO_URI else config.MONGO_URI
            print(f"DEBUG: Connecting to MongoDB: ...@{masked_uri}")
            
            # Connection options
            kwargs = {
                "serverSelectionTimeoutMS": 5000
            }
            
            # Use SSL/TLS only for Atlas or if explicitly requested
            if "mongodb+srv" in config.MONGO_URI or "ssl=true" in config.MONGO_URI.lower() or "tls=true" in config.MONGO_URI.lower():
                kwargs["tlsCAFile"] = certifi.where()
                kwargs["tls"] = True
                print("DEBUG: Using SSL/TLS for connection")
            
            self.client = MongoClient(config.MONGO_URI, **kwargs)
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
            print(f"DATABASE CONNECTION ERROR: {e}")
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
        if "report_id" not in report_data:
            import random
            import string
            import datetime
            # Generate human-readable unique ID: ET-[MONTH][RANDOM]
            # e.g., ET-04A1Z
            month = datetime.datetime.now().strftime("%m")
            suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            report_data["report_id"] = f"ET-{month}{suffix}"
        return self.reports.insert_one(report_data)

    @safe_execute
    def add_or_increment_report(self, report_data):
        import datetime
        
        # Search criteria for "same" issue
        query = {
            "pincode": report_data.get("pincode"),
            "locality": report_data.get("locality"),
            "topic_id": report_data.get("topic_id"),
            "issue_type": report_data.get("issue_type"),
            "status": "Open"
        }
        
        existing = self.reports.find_one(query)
        if existing:
            # Increment frequency and update timestamp
            return self.reports.update_one(
                {"_id": existing["_id"]},
                {
                    "$inc": {"frequency": 1},
                    "$set": {"last_updated": datetime.datetime.now()}
                }
            )
        else:
            # Add new report with frequency 1
            report_data["frequency"] = 1
            report_data["last_updated"] = datetime.datetime.now()
            return self.add_report(report_data)

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
    def get_all_active_areas(self):
        # Get formal areas
        areas = {a["area_id"]: a for a in self.areas.find()}
        
        # Get areas from reports and users that might not be in formal list
        active_ids = set(self.db.reports.distinct("area_id") + self.db.users.distinct("area_id"))
        for aid in active_ids:
            if aid and aid not in areas:
                # Try to find area name from latest report
                latest = self.db.reports.find_one({"area_id": aid}, sort=[("timestamp", -1)])
                name = latest.get("area_name") if latest else aid
                areas[aid] = {"area_id": aid, "area_name": name, "current_score": 100}
        
        return list(areas.values())

    @safe_execute
    def get_area_score(self, area_id):
        area = self.areas.find_one({"area_id": area_id})
        return area.get("current_score", 100) if area else 100

    @safe_execute
    def update_area_score(self, area_id, score_delta, area_name=None):
        name = area_name if area_name else area_id
        # Ensure area exists with default score
        self.areas.update_one(
            {"area_id": area_id},
            {"$setOnInsert": {"current_score": 100, "is_active": True, "area_name": name}},
            upsert=True
        )
        # Apply the delta
        if score_delta != 0:
            return self.areas.update_one(
                {"area_id": area_id},
                {"$inc": {"current_score": score_delta}}
            )
        return True

    @safe_execute
    def add_nudge(self, nudge_data):
        return self.nudges.insert_one(nudge_data)

    @safe_execute
    def get_nudges(self, dept_id):
        return list(self.nudges.find({"dept_id": dept_id.lower()}).sort("timestamp", -1))

    @safe_execute
    def add_support_request(self, request_data):
        return self.db["support_requests"].insert_one(request_data)

    @safe_execute
    def get_support_requests(self):
        return list(self.db["support_requests"].find().sort("timestamp", -1))

# Global database instance
db = Database()
