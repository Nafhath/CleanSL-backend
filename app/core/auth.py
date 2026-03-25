from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.supabase_client import supabase
from app.core.security import decode_access_token


bearer_scheme = HTTPBearer(auto_error=False)


def require_admin_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    payload = decode_access_token(credentials.credentials)
    admin_id = payload.get("sub")
    email = payload.get("email")
    role = payload.get("role")

    if not admin_id or role not in {"admin", "authority"}:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )

    rows = (
        supabase.table("admin_users")
        .select("id,email,full_name,role,is_active")
        .eq("id", admin_id)
        .eq("email", email)
        .limit(1)
        .execute()
        .data
        or []
    )

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin account not found.",
        )

    admin_user = rows[0]
    if not admin_user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive.",
        )

    return admin_user
