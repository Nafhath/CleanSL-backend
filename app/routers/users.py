from fastapi import APIRouter
from pydantic import BaseModel

from app.core.supabase_client import supabase

class LoginPayload(BaseModel):
    email: str
    password: str

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("")
def read_users():
    rows = supabase.table("users").select("*").order("created_at", desc=True).execute().data or []
    return rows


@router.get("/role/{role}")
def read_users_by_role(role: str):
    rows = supabase.table("users").select("*").eq("role", role).order("created_at", desc=True).execute().data or []
    return rows

@router.post("/auth/login")
def login(payload: LoginPayload):
    return {
        "success": True,
        "token": "admin_session_placeholder",
        "user": {"email": payload.email, "role": "admin", "name": payload.email.split("@")[0] or "Admin"}
    }
