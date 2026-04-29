import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from db.mongo import db
import datetime

def inject_hotspot_data():
    print("[Manual Injection] Creating a guaranteed hotspot in Indiranagar...")
    
    # Target Area: Indiranagar (area_1)
    # Target Location: Indiranagar Metro Station - Pillar 15
    
    target_area_id = "area_1"
    target_loc = "Indiranagar Metro Station - Pillar 15"
    
    # Add 8 identical reports to this location
    for i in range(8):
        report = {
            "report_id": f"HS-TEST-{i}",
            "user_id": 8888000 + i,
            "area_id": target_area_id,
            "area_name": "Indiranagar",
            "topic_id": "water_id",
            "issue_type": "Severe Leakage",
            "location": target_loc,
            "status": "Open",
            "timestamp": datetime.datetime.now() - datetime.timedelta(hours=i*5),
            "impact_value": 500
        }
        db.add_report(report)
        
    print(f"[Success] Injected 8 reports into '{target_loc}' for {target_area_id}.")

if __name__ == "__main__":
    inject_hotspot_data()
