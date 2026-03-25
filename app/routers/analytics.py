from fastapi import APIRouter, Depends
from app.core.auth import require_admin_user
from app.services.analytics import get_dashboard_summary

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary")
def read_dashboard_summary(_admin=Depends(require_admin_user)):
    try:
        data = get_dashboard_summary()
        return {
            "stats": {
                "totalPickups": data.get("completed_tasks", 0),
                "missedPickups": data.get("total_complaints", 0),
                "activeTrucks": data.get("active_drivers", 0),
                "newComplaints": data.get("pending_complaints", 0),
                "efficiency": "0%" if data.get("total_tasks", 0) == 0 else f"{round((data.get('completed_tasks', 0) / max(data.get('total_tasks', 1), 1)) * 100)}%"
            },
            "operations": []
        }
    except Exception as e:
        print("Error fetching analytics:", e)

    return {
        "stats": {
            "totalPickups": 0,
            "missedPickups": 0,
            "activeTrucks": 0,
            "newComplaints": 0,
            "efficiency": "0%"
        },
        "operations": []
    }

@router.get("/monthly-trends")
def read_monthly_trends(_admin=Depends(require_admin_user)):
    return []

@router.get("/waste-distribution")
def read_waste_distribution(_admin=Depends(require_admin_user)):
    return []
