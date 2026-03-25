from fastapi import APIRouter
from pydantic import BaseModel

class LoginPayload(BaseModel):
    email: str
    password: str

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("")
def read_users():
    return [
        { "_id": "1", "role": "driver", "firstName": "John", "lastName": "Smith", "location": "Ward 1" },
        { "_id": "2", "role": "driver", "firstName": "Sarah", "lastName": "Johnson", "location": "Ward 2" },
        { "_id": "3", "role": "admin", "firstName": "Admin", "lastName": "User", "location": "HQ" }
    ]

@router.post("/auth/login")
def login(payload: LoginPayload):
    return {
        "success": True,
        "token": "mvp_mock_token_123",
        "user": {"email": payload.email, "role": "admin", "name": "MVP Admin"}
    }
