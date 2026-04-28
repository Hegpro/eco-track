import sys
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Add parent directory to path to import db
sys.path.append(str(Path(__file__).parent.parent))
from db.mongo import db

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="dashboard/static"), name="static")
templates = Jinja2Templates(directory="dashboard/templates")

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    # Fetch stats
    total_users = db.users.count_documents({})
    total_reports = db.reports.count_documents({})
    recent_reports = list(db.reports.find().sort("timestamp", -1).limit(10))
    
    # Format reports for display
    for r in recent_reports:
        r["_id"] = str(r["_id"])
        r["timestamp"] = r["timestamp"].strftime("%Y-%m-%d %H:%M")
        
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "total_users": total_users,
            "total_reports": total_reports,
            "recent_reports": recent_reports
        }
    )

@app.get("/api/stats")
async def get_stats():
    users = db.users.count_documents({})
    reports = db.reports.count_documents({})
    return {"users": users, "reports": reports}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
