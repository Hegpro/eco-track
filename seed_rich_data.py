from db.mongo import db
import datetime
import random

def seed_rich_data():
    print("[Seed] Initializing high-density environmental data...")
    
    # 1. Reset and Create Diverse Areas
    db.db.areas.delete_many({})
    area_names = [
        "Indiranagar", "Koramangala", "HSR Layout", "Whitefield", 
        "Jayanagar", "Malleshwaram", "JP Nagar", "Frazer Town",
        "BTM Layout", "Banashankari", "Rajajinagar", "Sadashivanagar"
    ]
    
    areas = []
    for i, name in enumerate(area_names):
        area_obj = {
            "area_id": f"area_{i+1}",
            "area_name": name,
            "pincode": f"5600{random.randint(10, 99)}",
            "is_active": True,
            "current_score": random.randint(65, 95),
            "registered_at": datetime.datetime.now() - datetime.timedelta(days=60)
        }
        db.db.areas.insert_one(area_obj)
        areas.append(area_obj)
    
    print(f"[Seed] Created {len(areas)} areas.")

    # 2. Sample Categories & Issues
    categories = [
        {"key": "water", "name": "Water Resources", "id": "water_id", "issues": ["Pipeline Burst", "Severe Leakage", "Low Pressure", "Water Contamination", "Illegal Connection"]},
        {"key": "electricity", "name": "Electricity", "id": "electricity_id", "issues": ["Transformer Sparking", "Street Light Out", "Low Voltage", "Power Line Hanging", "Meter Fault"]},
        {"key": "sewage", "name": "Waste Management", "id": "sewage_id", "issues": ["Blocked Drain", "Bin Overflowing", "Open Manhole", "Illegal Dumping", "Stagnant Water"]}
    ]
    
    localities_pool = [
        "Main Road", "2nd Cross", "8th Main", "Market Square", "Park View Lane", 
        "Service Road", "Temple Street", "College Road", "Metro Station Exit"
    ]
    
    statuses = ["Open", "Open", "Open", "Open", "Resolved", "Resolved"] # ~66% Open
    
    # Clear existing reports
    db.db.reports.delete_many({})
    db.db.nudges.delete_many({})
    print("[Seed] Cleared old reports and nudges.")

    # 3. Generate 150 Reports over 30 days
    print("[Seed] Generating 150 reports across 30-day timeline...")
    count = 0
    
    # Pre-select some hotspot locations per area to ensure they repeat
    hotspot_map = {area["area_id"]: random.sample(localities_pool, 2) for area in areas}

    for i in range(150):
        cat = random.choice(categories)
        area = random.choice(areas)
        
        # 40% chance to be a hotspot location
        if random.random() < 0.4:
            loc = random.choice(hotspot_map[area["area_id"]])
        else:
            loc = random.choice(localities_pool)
            
        status = random.choice(statuses)
        issue = random.choice(cat["issues"])
        
        # Time within last 30 days
        # More reports in the last 5 days
        if random.random() < 0.6:
            days_ago = random.randint(0, 5)
        else:
            days_ago = random.randint(6, 30)
            
        time_diff = random.randint(0, 1440) # Random minute in that day
        timestamp = datetime.datetime.now() - datetime.timedelta(days=days_ago, minutes=time_diff)
        
        report = {
            "user_id": 9999000 + i,
            "area_id": area["area_id"],
            "area_name": area["area_name"],
            "topic_id": cat["id"],
            "issue_type": issue,
            "location": f"{loc}, Near Landmark {random.randint(1, 10)}",
            "status": status,
            "timestamp": timestamp,
            "impact_value": random.randint(50, 800) if cat["key"] == "water" else 0
        }
        
        if status == "Resolved":
            # Resolve time between 1 and 48 hours later
            res_delay = random.randint(60, 2880)
            report["resolved_at"] = timestamp + datetime.timedelta(minutes=res_delay)
            report["resolved_by"] = random.choice(["elec_staff", "water_staff", "sewage_staff", "admin"])
        
        db.add_report(report)
        count += 1

    print(f"[Seed] Successfully added {count} diverse incidents with historical data.")

if __name__ == "__main__":
    seed_rich_data()
