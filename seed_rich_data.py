from db.mongo import db
import datetime
import random

def seed_rich_data():
    print("[Seed] Generating high-density feed data for Eco-Track...")
    
    # 1. Ensure Areas exist
    areas = list(db.db.areas.find())
    if not areas:
        print("[Error] No areas found. Run seed.py first.")
        return
    
    # 2. Sample Data
    categories = [
        {"key": "water", "name": "Water Resources", "id": "water_id", "issues": ["Pipeline Burst", "Severe Leakage", "Low Pressure", "Water Contamination"]},
        {"key": "electricity", "name": "Electricity", "id": "electricity_id", "issues": ["Transformer Sparking", "Street Light Out", "Low Voltage", "Power Line Hanging"]},
        {"key": "sewage", "name": "Waste Management", "id": "sewage_id", "issues": ["Blocked Drain", "Bin Overflowing", "Open Manhole", "Illegal Dumping"]}
    ]
    
    localities = ["Indiranagar 100ft Rd", "HAL 2nd Stage", "Domlur Layout", "Koramangala 4th Block", "Binnamangala"]
    statuses = ["Open", "Open", "Open", "Resolved"] # 75% Open, 25% Resolved
    
    # Clear existing reports for a fresh look
    db.db.reports.delete_many({})
    print("[Seed] Cleared old reports.")

    # 3. Generate 20 Reports
    for i in range(20):
        cat = random.choice(categories)
        area = random.choice(areas)
        status = random.choice(statuses)
        issue = random.choice(cat["issues"])
        loc = random.choice(localities)
        
        # Time within last 72 hours (to test delayed issues > 24h)
        time_diff = random.randint(0, 4320)
        timestamp = datetime.datetime.now() - datetime.timedelta(minutes=time_diff)
        
        report = {
            "user_id": 9999000 + i,
            "area_id": area["area_id"],
            "area_name": area["area_name"],
            "topic_id": cat["id"],
            "issue_type": issue,
            "location": f"{loc}, Near Landmark {random.randint(1, 20)}",
            "status": status,
            "timestamp": timestamp,
            "impact_value": random.randint(50, 500) if cat["key"] == "water" else 0
        }
        
        if status == "Resolved":
            report["resolved_at"] = timestamp + datetime.timedelta(minutes=random.randint(30, 240))
            report["resolved_by"] = "System Admin"

        db.add_report(report)

    print(f"[Seed] Successfully added 20 diverse incidents to the feed.")

if __name__ == "__main__":
    seed_rich_data()
