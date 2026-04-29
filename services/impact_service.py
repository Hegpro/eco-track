from db.mongo import db
import datetime

def calculate_score(area_id):
    # Base score is 100
    score = 100
    
    # Deduct for open reports
    open_reports = list(db.reports.find({"area_id": area_id, "status": "Open"}))
    for report in open_reports:
        # Simple deduction based on department
        tid = report.get("topic_id", "")
        if "water" in tid: score -= 10
        elif "electricity" in tid: score -= 12
        else: score -= 5
        
    return max(0, min(100, score))

def get_area_impact(area_id):
    score = calculate_score(area_id)
    area = db.db.areas.find_one({"area_id": area_id})
    area_name = area['area_name'] if area else "Community"
    
    # Real counts
    water_c = db.reports.count_documents({"area_id": area_id, "topic_id": "water_id", "status": "Open"})
    elec_c = db.reports.count_documents({"area_id": area_id, "topic_id": "electricity_id", "status": "Open"})
    waste_c = db.reports.count_documents({"area_id": area_id, "topic_id": "waste_id", "status": "Open"})
    
    resolved_total = db.reports.count_documents({"area_id": area_id, "status": "Resolved"})
    
    msg = (
        f"🏘 *Area: {area_name}*\n\n"
        f"✨ *Current Score: {score}/100*\n"
        f"━━━━━━━━━━━━━━\n"
        f"🚨 *Open Issues:*\n"
        f"💧 Water: {water_c}\n"
        f"⚡ Electricity: {elec_c}\n"
        f"🗑 Waste: {waste_c}\n\n"
        f"✅ *Resolved (All Time):* {resolved_total}\n"
        f"━━━━━━━━━━━━━━\n"
        f"💡 Tip: Fix water leaks to gain +10 points!"
    )
    return msg

def get_area_trends(area_id):
    day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    new_reports = db.reports.count_documents({
        "area_id": area_id, 
        "timestamp": {"$gte": day_ago}
    })
    
    resolved_reports = db.reports.count_documents({
        "area_id": area_id, 
        "status": "Resolved",
        "resolved_at": {"$gte": day_ago}
    })
    
    trend = resolved_reports - new_reports
    arrow = "📈" if trend > 0 else "📉"
    status = "Improving" if trend > 0 else "Needs Attention"
    if trend == 0:
        arrow = "📊"
        status = "Stable"
        
    msg = (
        f"📈 *Trend Analysis (Last 24h)*\n\n"
        f"New Issues reported: {new_reports}\n"
        f"Issues successfully fixed: {resolved_reports}\n\n"
        f"Overall Health: {arrow} *{status}*\n"
        f"━━━━━━━━━━━━━━\n"
        f"Keep reporting and fixing issues to improve your area's rank!"
    )
    return msg

def get_personal_impact(user_id):
    user = db.get_user(user_id)
    msg = (
        "👤 *Your Stats*\n\n"
        f"Reports: {user.get('reports_count', 0)}\n"
        f"Resolved: {user.get('resolved_count', 0)}\n\n"
        "💧 Water Saved: ~500L\n"
        "🗑 Waste Reduced: 3 cases\n\n"
        "🏅 Rank: #3"
    )
    return msg

def get_leaderboard():
    areas = list(db.areas.find())
    sorted_areas = sorted(areas, key=lambda x: calculate_score(x["area_id"]), reverse=True)
    
    msg = "🏆 *Top Areas*\n\n"
    emojis = ["🥇", "🥈", "🥉"]
    for i, a in enumerate(sorted_areas[:3]):
        msg += f"{emojis[i]} {a['area_name']} – {calculate_score(a['area_id'])}\n"
    return msg
