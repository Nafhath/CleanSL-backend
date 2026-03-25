from fastapi import APIRouter, Depends
from app.core.auth import require_admin_user
from app.services.anomalies import generate_anomalies

router = APIRouter(prefix="/violations", tags=["Violations"])

@router.get("")
def read_violations(_admin=Depends(require_admin_user)):
    return generate_anomalies()

@router.get("/stats/overview")
def read_violations_stats(_admin=Depends(require_admin_user)):
    anomalies = generate_anomalies()
    total = len(anomalies)
    pending = len([a for a in anomalies if a["status"] == "Pending"])
    confirmed = len([a for a in anomalies if a["status"] == "Confirmed"])
    
    return [
        { "label": "Total Violations", "value": str(total), "trend": "live", "color": "text-theme-text" },
        { "label": "Pending Review", "value": str(pending), "trend": "live", "color": "text-theme-accent" },
        { "label": "Confirmed", "value": str(confirmed), "trend": "live", "color": "text-emerald-500" },
        { "label": "Resolved", "value": str(max(total - pending - confirmed, 0)), "trend": "live", "color": "text-purple-500" }
    ]
