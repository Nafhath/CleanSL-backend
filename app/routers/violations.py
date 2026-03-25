from fastapi import APIRouter
from app.services.anomalies import generate_anomalies

router = APIRouter(prefix="/violations", tags=["Violations"])

@router.get("")
def read_violations():
    return generate_anomalies()

@router.get("/stats/overview")
def read_violations_stats():
    anomalies = generate_anomalies()
    total = len(anomalies)
    pending = len([a for a in anomalies if a["status"] == "Pending"])
    confirmed = len([a for a in anomalies if a["status"] == "Confirmed"])
    
    return [
        { "label": "Total Violations", "value": str(total), "trend": "+12%", "color": "text-theme-text" },
        { "label": "Pending Review", "value": str(pending), "trend": "+3%", "color": "text-theme-accent" },
        { "label": "Confirmed", "value": str(confirmed), "trend": "-5%", "color": "text-emerald-500" },
        { "label": "Resolved", "value": str(max(total - pending - confirmed, 0)), "trend": "+1%", "color": "text-purple-500" }
    ]
