from app.core.supabase_client import supabase
from typing import Any, cast


def get_dashboard_summary():
    addresses = supabase.table("addresses").select("id", count="exact").execute()  # type: ignore
    complaints = supabase.table("complaints").select("id,status", count="exact").execute()  # type: ignore
    tasks = supabase.table("collection_tasks").select("id,status", count="exact").execute()  # type: ignore
    drivers = supabase.table("driver_profiles").select("user_id,status").execute()

    complaint_rows = cast(list[dict[str, Any]], complaints.data or [])
    task_rows = cast(list[dict[str, Any]], tasks.data or [])
    driver_rows = cast(list[dict[str, Any]], drivers.data or [])

    return {
        "total_addresses": addresses.count or 0,
        "total_complaints": complaints.count or 0,
        "pending_complaints": len([c for c in complaint_rows if c.get("status") == "pending"]),
        "resolved_complaints": len([c for c in complaint_rows if c.get("status") == "resolved"]),
        "total_tasks": tasks.count or 0,
        "completed_tasks": len([t for t in task_rows if t.get("status") == "completed"]),
        "active_drivers": len([d for d in driver_rows if d.get("status") == "on_duty"]),
    }

