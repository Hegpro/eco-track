from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sys
from pathlib import Path
import datetime

# Add parent directory to path to import db
sys.path.append(str(Path(__file__).parent.parent))
from db.mongo import db

app = FastAPI()

app.mount("/static", StaticFiles(directory="dashboard/static"), name="static")
templates = Jinja2Templates(directory="dashboard/templates")

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    total_users = db.users.count_documents({})
    total_reports = db.reports.count_documents({})
    open_reports = db.reports.count_documents({"status": "Open"})
    
    raw_reports = list(db.reports.find().sort("timestamp", -1).limit(20))
    recent_reports = []
    
    # Format reports into a clean list of dicts for the template
    for r in raw_reports:
        ts = r.get("timestamp")
        if isinstance(ts, datetime.datetime):
            ts_str = ts.strftime("%Y-%m-%d %H:%M")
        else:
            ts_str = "Recently"
            
        dept = str(r.get("topic_id", "General")).split("_")[0].title()
        
        formatted_report = {
            "id": str(r.get("_id")),
            "status": str(r.get("status", "Open")),
            "display_dept": dept,
            "issue_text": r.get("issue_type", r.get("subtopic", "Incident")),
            "location": r.get("location", "Unknown Location"),
            "impact": r.get("impact_value", r.get("quantity", 0)),
            "timestamp": ts_str,
            "intensity_class": dept.lower(),
            "image_id": r.get("image_id")
        }
        recent_reports.append(formatted_report)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "total_users": total_users,
            "total_reports": total_reports,
            "open_reports": open_reports,
            "recent_reports": recent_reports
        }
    )

@app.get("/api/stats")
async def get_stats():
    total_users = db.users.count_documents({})
    total_reports = db.reports.count_documents({})
    open_reports = db.reports.count_documents({"status": "Open"})
    
    # Dept counts
    electrical = db.reports.count_documents({"topic_id": "electricity_id", "status": "Open"})
    sewage = db.reports.count_documents({"topic_id": "sewage_id", "status": "Open"})
    plumbing = db.reports.count_documents({"topic_id": "water_id", "status": "Open"})

    return {
        "total_users": total_users,
        "total_reports": total_reports,
        "open_reports": open_reports,
        "depts": {
            "electrical": electrical,
            "sewage": sewage,
            "plumbing": plumbing
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
