
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path
import datetime

# Add parent directory to path to import db
sys.path.append(str(Path(__file__).parent.parent))
from db.mongo import db

app = FastAPI(title="Eco-Track API")

# Enable CORS for React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    print(f"GLOBAL ERROR: {exc}")
    print(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"message": str(exc), "traceback": traceback.format_exc()},
    )

from fastapi.responses import JSONResponse

@app.get("/api/overview")
async def get_overview():
    try:
        now = datetime.datetime.now()
        
        # 7-day historical data
        historical = []
        for i in range(7):
            day = now - datetime.timedelta(days=6-i)
            start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
            count = db.reports.count_documents({"timestamp": {"$gte": start, "$lte": end}})
            historical.append({"name": day.strftime("%a").upper(), "value": count})

        # Departmental efficiency
        def get_eff(topic_id):
            total = db.reports.count_documents({"topic_id": topic_id})
            resolved = db.reports.count_documents({"topic_id": topic_id, "status": "Resolved"})
            return round((resolved / total * 100), 1) if total > 0 else 0

        threshold = now - datetime.timedelta(hours=24)

        return {
            "stats": {
                "users": db.users.count_documents({}),
                "total_reports": db.reports.count_documents({}),
                "pending": db.reports.count_documents({"status": "Open"}),
                "resolved": db.reports.count_documents({"status": "Resolved"}),
                "delayed": db.reports.count_documents({"status": "Open", "timestamp": {"$lt": threshold}}),
                "eco_score": 84,
            },
            "dept_pending": {
                "electrical": db.reports.count_documents({"topic_id": "electricity_id", "status": "Open"}),
                "water": db.reports.count_documents({"topic_id": "water_id", "status": "Open"}),
                "sewage": db.reports.count_documents({"topic_id": "sewage_id", "status": "Open"}),
            },
            "dept_delayed": {
                "electrical": db.reports.count_documents({"topic_id": "electricity_id", "status": "Open", "timestamp": {"$lt": threshold}}),
                "water": db.reports.count_documents({"topic_id": "water_id", "status": "Open", "timestamp": {"$lt": threshold}}),
                "sewage": db.reports.count_documents({"topic_id": "sewage_id", "status": "Open", "timestamp": {"$lt": threshold}}),
            },
            "efficiency": {
                "electrical": get_eff("electricity_id"),
                "water": get_eff("water_id"),
                "sewage": get_eff("sewage_id"),
            },
            "historical_data": historical
        }
    except Exception as e:
        print(f"Overview error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports")
async def get_reports(dept: str = None, status: str = None, delayed: bool = False, search: str = None):
    query = {}
    
    if search:
        # Search by report_id (case-insensitive prefix search)
        query["report_id"] = {"$regex": f"{search}", "$options": "i"}
    else:
        if dept: query["topic_id"] = f"{dept}_id"
        if status: query["status"] = status
    
    if delayed:
        threshold = datetime.datetime.now() - datetime.timedelta(hours=24)
        query["status"] = "Open"
        query["timestamp"] = {"$lt": threshold}
    
    reports = list(db.reports.find(query).sort("timestamp", -1).limit(50))
    for r in reports:
        r["_id"] = str(r["_id"])
        if isinstance(r.get("timestamp"), datetime.datetime):
            r["timestamp"] = r["timestamp"].isoformat()
        if isinstance(r.get("resolved_at"), datetime.datetime):
            r["resolved_at"] = r["resolved_at"].isoformat()
    return reports

@app.post("/api/reports/{report_id}/resolve")
async def resolve_report(report_id: str, request: Request):
    data = await request.json()
    staff_id = data.get("staff_id", "admin")
    
    try:
        from bson import ObjectId
        res = db.reports.update_one(
            {"_id": ObjectId(report_id)},
            {"$set": {
                "status": "Resolved",
                "resolved_at": datetime.datetime.now(),
                "resolved_by": staff_id
            }}
        )
        if res.matched_count == 0:
            raise HTTPException(status_code=404, detail="Report not found")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/areas")
async def get_areas():
    areas = list(db.areas.find())
    for a in areas:
        a["_id"] = str(a["_id"])
        a["name"] = a.get("area_name", "Unknown Area")
    return areas

@app.get("/api/areas/{area_id}/stats")
async def get_area_stats(area_id: str):
    area = db.areas.find_one({"area_id": area_id})
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    pending = db.reports.count_documents({"area_id": area_id, "status": "Open"})
    resolved = db.reports.count_documents({"area_id": area_id, "status": "Resolved"})
    
    score = area.get("current_score", 100)
    
    return {
        "name": area.get("area_name", "Unknown"),
        "score": score,
        "pending": pending,
        "resolved": resolved,
        "impact": resolved * 200
    }

@app.post("/api/nudges")
async def create_nudge(request: Request):
    data = await request.json()
    data["timestamp"] = datetime.datetime.now()
    db.add_nudge(data)
    return {"status": "success"}

@app.get("/api/nudges")
async def get_nudges(dept: str):
    nudges = db.get_nudges(dept)
    for n in nudges:
        n["_id"] = str(n["_id"])
        if isinstance(n.get("timestamp"), datetime.datetime):
            n["timestamp"] = n["timestamp"].isoformat()
    return nudges

@app.get("/api/areas/{area_id}/hotspots")
async def get_area_hotspots(area_id: str):
    pipeline = [
        {"$match": {"area_id": area_id}},
        {"$group": {
            "_id": "$location",
            "count": {"$sum": 1},
            "issue_types": {"$addToSet": "$issue_type"}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 3}
    ]
    hotspots = list(db.reports.aggregate(pipeline))
    return [
        {
            "location": h["_id"],
            "count": h["count"],
            "primary_issue": h["issue_types"][0] if h["issue_types"] else "Multiple"
        } for h in hotspots
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
