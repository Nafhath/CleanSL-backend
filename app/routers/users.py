from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.auth import require_admin_user
from app.core.security import create_access_token, verify_password
from app.core.supabase_client import supabase


class LoginPayload(BaseModel):
    email: str
    password: str


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
def read_users(_admin=Depends(require_admin_user)):
    rows = supabase.table("users").select("*").order("created_at", desc=True).execute().data or []
    return rows


@router.get("/role/{role}")
def read_users_by_role(role: str, _admin=Depends(require_admin_user)):
    rows = supabase.table("users").select("*").eq("role", role).order("created_at", desc=True).execute().data or []
    return rows


@router.post("/auth/login")
def login(payload: LoginPayload):
    rows = (
        supabase.table("admin_users")
        .select("id,email,full_name,role,password_hash,is_active")
        .eq("email", payload.email.strip().lower())
        .limit(1)
        .execute()
        .data
        or []
    )

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials.",
        )

    admin_user = rows[0]
    if not admin_user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive.",
        )

    if not verify_password(payload.password, admin_user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials.",
        )

    supabase.table("admin_users").update(
        {"last_login_at": datetime.now(timezone.utc).isoformat()}
    ).eq("id", admin_user["id"]).execute()
    token = create_access_token(
        subject=admin_user["id"],
        email=admin_user["email"],
        role=admin_user["role"],
    )

    return {
        "success": True,
        "token": token,
        "user": {
            "id": admin_user["id"],
            "email": admin_user["email"],
            "role": admin_user["role"],
            "name": admin_user.get("full_name") or admin_user["email"].split("@")[0] or "Admin",
        },
    }
