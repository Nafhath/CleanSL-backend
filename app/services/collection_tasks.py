from datetime import datetime, timezone
from fastapi import HTTPException
from app.core.supabase_client import supabase
from typing import Any, cast

TABLE = "collection_tasks"

def list_tasks(status: str | None = None, driver_id: str | None = None):
    query = supabase.table(TABLE).select("*")
    if status:
        query = query.eq("status", status)
    if driver_id:
        query = query.eq("driver_id", driver_id)
    return query.order("scheduled_date", desc=False).execute().data


def get_task(task_id: str):
    response = supabase.table(TABLE).select("*").eq("id", task_id).single().execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Task not found")
    return response.data


def create_task(payload: dict):
    return supabase.table(TABLE).insert(payload).execute().data[0]


def update_task(task_id: str, payload: dict):
    payload["updated_at"] = datetime.now(timezone.utc).isoformat()
    existing = supabase.table(TABLE).select("id").eq("id", task_id).execute().data
    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")

    result = supabase.table(TABLE).update(payload).eq("id", task_id).execute().data
    if not result:
        raise HTTPException(status_code=500, detail="Task update failed")

    updated = cast(dict[str, Any], result[0])

    if payload.get("status") == "completed":
        address_id = updated.get("address_id")
        if address_id:
            supabase.table("addresses").update(
                {"last_collection_at": datetime.now(timezone.utc).isoformat()}
            ).eq("id", address_id).execute()

    return updated



def delete_task(task_id: str):
    existing = supabase.table(TABLE).select("id").eq("id", task_id).execute().data
    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")
    supabase.table(TABLE).delete().eq("id", task_id).execute()
    return {"message": "Task deleted successfully"}