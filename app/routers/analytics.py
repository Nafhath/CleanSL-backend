from fastapi import APIRouter
from app.services.analytics import get_dashboard_summary

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary")
def read_dashboard_summary():
    try:
        data = get_dashboard_summary()
        if data:
            # Map Python backend schema to React frontend schema
            return {
                "stats": {
                    "totalPickups": data.get("completed_tasks", 154),
                    "missedPickups": data.get("total_complaints", 3),
                    "activeTrucks": data.get("active_drivers", 8),
                    "newComplaints": data.get("pending_complaints", 12),
                    "efficiency": "88%"  # Hardcoded MVP
                },
                "operations": [
                    {"id": 1, "event": "Live Supabase Connection", "detail": "Data synchronization active", "time": "Just now", "status": "Verified", "color": "green"}
                ]
            }
    except Exception as e:
        print("Error fetching analytics:", e)

    return {
        "stats": {
            "totalPickups": 154,
            "missedPickups": 3,
            "activeTrucks": 8,
            "newComplaints": 12,
            "efficiency": "88%"
        },
        "operations": [
            {"id": 1, "event": "Truck T-01 Departed", "detail": "Ward 07 Collection", "time": "2 mins ago", "status": "Moving", "color": "blue"},
            {"id": 2, "event": "New Complaint", "detail": "Missed pickup at 45 Flower Rd", "time": "15 mins ago", "status": "Pending", "color": "yellow"}
        ]
    }

@router.get("/monthly-trends")
def read_monthly_trends():
    return [
        { "name": "Jan", "value": 3100 },
        { "name": "Feb", "value": 3400 },
        { "name": "Mar", "value": 3200 },
        { "name": "Apr", "value": 4150 }
    ]

@router.get("/waste-distribution")
def read_waste_distribution():
    return [
        { "name": "Plastic", "value": 40, "fill": "#2D5A27" },
        { "name": "Paper", "value": 20, "fill": "#5DAE54" },
        { "name": "Metal", "value": 15, "fill": "#A3D99F" },
        { "name": "Organic", "value": 25, "fill": "#E9F2E8" }
    ]