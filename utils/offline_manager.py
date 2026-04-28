import json
import os
import datetime
from db.mongo import db

OFFLINE_FILE = "offline_queue.json"

def queue_offline_report(report_data):
    """Saves a report locally if the DB is unreachable."""
    queue = []
    if os.path.exists(OFFLINE_FILE):
        with open(OFFLINE_FILE, "r") as f:
            try:
                queue = json.load(f)
            except:
                queue = []
    
    # Convert datetime to string for JSON
    report_data["timestamp"] = datetime.datetime.now().isoformat()
    queue.append(report_data)
    
    with open(OFFLINE_FILE, "w") as f:
        json.dump(queue, f, indent=4)
    
    return len(queue)

def sync_offline_reports():
    """Tries to push offline reports to MongoDB."""
    if not os.path.exists(OFFLINE_FILE):
        return 0
        
    with open(OFFLINE_FILE, "r") as f:
        try:
            queue = json.load(f)
        except:
            return 0
            
    synced_count = 0
    remaining = []
    
    for report in queue:
        try:
            # Convert string back to datetime
            report["timestamp"] = datetime.datetime.fromisoformat(report["timestamp"])
            db.add_report(report)
            synced_count += 1
        except Exception:
            remaining.append(report)
            
    if remaining:
        with open(OFFLINE_FILE, "w") as f:
            json.dump(remaining, f, indent=4)
    else:
        os.remove(OFFLINE_FILE)
        
    return synced_count
