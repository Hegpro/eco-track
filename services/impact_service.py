from db.mongo import db
import datetime
from utils.constants import STATUS_GOOD, STATUS_HIGH

def get_area_impact(area_id):
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get all reports for this area today
    reports = list(db.reports.find({
        "area_id": area_id,
        "timestamp": {"$gte": today}
    }))
    
    if not reports:
        return "No reports yet for your area today."
        
    # Aggregate by topic
    topic_usage = {}
    for report in reports:
        topic_id = report["topic_id"]
        if topic_id not in topic_usage:
            topic = db.db.topics.find_one({"topic_id": topic_id})
            topic_usage[topic_id] = {
                "name": topic["name"] if topic else "Unknown",
                "unit": topic["unit"] if topic else "",
                "total": 0
            }
        topic_usage[topic_id]["total"] += report["quantity"]
        
    # Format summary
    area = db.db.areas.find_one({"area_id": area_id})
    summary = f"📍 *Area Impact: {area['area_name']}*\n"
    summary += f"📅 Date: {today.strftime('%Y-%m-%d')}\n\n"
    
    for tid, data in topic_usage.items():
        summary += f"🔹 {data['name']}: {data['total']} {data['unit']}\n"
        
    # Basic scoring logic (can be expanded)
    # If any usage > 100 (dummy threshold), show High
    is_high = any(d["total"] > 100 for d in topic_usage.values())
    status = STATUS_HIGH if is_high else STATUS_GOOD
    
    summary += f"\n📊 *Status:* {status}"
    if status == STATUS_HIGH:
        summary += "\n⚠️ Usage is higher than average. Consider conserving resources!"
    else:
        summary += "\n✅ Great job! Resource usage is within healthy limits."
        
    return summary
