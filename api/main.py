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
    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/overview")
async def get_overview():
    total_users = db.users.count_documents({})
    total_reports = db.reports.count_documents({})
    open_reports = db.reports.count_documents({"status": "Open"})
    resolved_reports = db.reports.count_documents({"status": "Resolved"})
    
    # Dept-wise pending
    depts = {
        "electrical": db.reports.count_documents({"topic_id": "electricity_id", "status": "Open"}),
        "water": db.reports.count_documents({"topic_id": "water_id", "status": "Open"}),
        "sewage": db.reports.count_documents({"topic_id": "sewage_id", "status": "Open"})
    }

    return {
        "stats": {
            "users": total_users,
            "total_reports": total_reports,
            "pending": open_reports,
            "resolved": resolved_reports
        },
        "dept_pending": depts
    }

@app.get("/api/reports")
async def get_reports(dept: str = None, status: str = None):
    query = {}
    if dept: query["topic_id"] = f"{dept}_id"
    if status: query["status"] = status
    
    reports = list(db.reports.find(query).sort("timestamp", -1).limit(50))
    for r in reports:
        r["_id"] = str(r["_id"])
        if isinstance(r.get("timestamp"), datetime.datetime):
            r["timestamp"] = r["timestamp"].isoformat()
    return reports

@app.post("/api/reports/{report_id}/resolve")
async def resolve_report(report_id: str, request: Request):
    data = await request.json()
    staff_id = data.get("staff_id", "admin")
    
    try:
        from bson import ObjectId
        res = db.db.reports.update_one(
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
    return areas

@app.get("/api/leaderboard")
async def get_leaderboard_stats():
    # Simple top 5 areas by score
    areas = list(db.areas.find().sort("current_score", -1).limit(5))
    return [{"name": a["area_name"], "score": a.get("current_score", 100)} for a in areas]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
