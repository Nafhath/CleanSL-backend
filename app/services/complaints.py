from fastapi import HTTPException
from app.core.supabase_client import supabase

TABLE = "complaints"

def list_complaints(status: str | None = None, priority: str | None = None):
    query = supabase.table(TABLE).select("*")
    if status:
        query = query.eq("status", status)
    if priority:
        query = query.eq("priority_level", priority)
    return query.order("created_at", desc=True).execute().data


def get_complaint(complaint_id: str):
    response = supabase.table(TABLE).select("*").eq("id", complaint_id).single().execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return response.data


def create_complaint(payload: dict):
    return supabase.table(TABLE).insert(payload).execute().data[0]


def update_complaint(complaint_id: str, payload: dict):
    existing = supabase.table(TABLE).select("id").eq("id", complaint_id).execute().data
    if not existing:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return supabase.table(TABLE).update(payload).eq("id", complaint_id).execute().data[0]


def delete_complaint(complaint_id: str):
    existing = supabase.table(TABLE).select("id").eq("id", complaint_id).execute().data
    if not existing:
        raise HTTPException(status_code=404, detail="Complaint not found")
    supabase.table(TABLE).delete().eq("id", complaint_id).execute()
    return {"message": "Complaint deleted successfully"}