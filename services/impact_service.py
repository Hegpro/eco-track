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
    
    # Mock counts
    water_c = db.reports.count_documents({"area_id": area_id, "topic_id": "water_id", "status": "Open"})
    elec_c = db.reports.count_documents({"area_id": area_id, "topic_id": "electricity_id", "status": "Open"})
    waste_c = db.reports.count_documents({"area_id": area_id, "topic_id": "waste_id", "status": "Open"})
    
    msg = (
        f"🏘 *Area: {area['area_name']}*\n\n"
        f"Score: {score}/100\n\n"
        f"💧 Water: {water_c} issues\n"
        f"⚡ Electricity: {elec_c} issues\n"
        f"🗑 Waste: {waste_c} issues\n\n"
        f"Trend: ↓ -8 today"
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
