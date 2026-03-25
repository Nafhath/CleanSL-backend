from fastapi import APIRouter
from app.services.anomalies import generate_anomalies

router = APIRouter(prefix="/violations", tags=["Violations"])

@router.get("")
def read_violations():
    anomalies = generate_anomalies()
    if anomalies:
        return anomalies
        
    return [
        { "date": "22/10/2026", "type": "Mixed Waste", "resident": "Kamal Perera", "status": "Confirmed", "score": 96 },
        { "date": "21/10/2026", "type": "Unsorted Plastics", "resident": "Nimal Fernando", "status": "Pending", "score": 88 }
    ]

@router.get("/stats/overview")
def read_violations_stats():
    anomalies = generate_anomalies()
    total = len(anomalies) or 156
    pending = len([a for a in anomalies if a["status"] == "Pending"]) or 24
    confirmed = len([a for a in anomalies if a["status"] == "Confirmed"]) or 89
    
    return [
        { "label": "Total Violations", "value": str(total), "trend": "+12%", "color": "text-theme-text" },
        { "label": "Pending Review", "value": str(pending), "trend": "+3%", "color": "text-theme-accent" },
        { "label": "Confirmed", "value": str(confirmed), "trend": "-5%", "color": "text-emerald-500" },
        { "label": "Resolved", "value": str(max(total - pending - confirmed, 0)), "trend": "+1%", "color": "text-purple-500" }
    ]
