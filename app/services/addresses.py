from fastapi import HTTPException
from app.core.supabase_client import supabase


TABLE = "addresses"


def list_addresses():
    return supabase.table(TABLE).select("*").execute().data


def get_address(address_id: str):
    response = supabase.table(TABLE).select("*").eq("id", address_id).single().execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Address not found")
    return response.data


def create_address(payload: dict):
    return supabase.table(TABLE).insert(payload).execute().data[0]


def update_address(address_id: str, payload: dict):
    existing = supabase.table(TABLE).select("id").eq("id", address_id).execute().data
    if not existing:
        raise HTTPException(status_code=404, detail="Address not found")
    return supabase.table(TABLE).update(payload).eq("id", address_id).execute().data[0]


def delete_address(address_id: str):
    existing = supabase.table(TABLE).select("id").eq("id", address_id).execute().data
    if not existing:
        raise HTTPException(status_code=404, detail="Address not found")
    supabase.table(TABLE).delete().eq("id", address_id).execute()
    return {"message": "Address deleted successfully"}