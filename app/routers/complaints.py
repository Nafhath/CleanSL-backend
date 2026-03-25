from fastapi import APIRouter, Depends, Query
from app.core.auth import require_admin_user
from app.models.schemas import ComplaintCreate, ComplaintUpdate
from app.services.complaints import list_complaints, get_complaint, create_complaint, update_complaint, delete_complaint

router = APIRouter(prefix="/complaints", tags=["Complaints"])

@router.get("")
def read_complaints(
    status: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    _admin=Depends(require_admin_user)
):
    return list_complaints(status, priority)

@router.get("/stats/overview")
def read_complaints_stats(_admin=Depends(require_admin_user)):
    complaints = list_complaints()
    pending = len([item for item in complaints if item.get("status") == "pending"])
    in_progress = len([item for item in complaints if item.get("status") in {"reviewed", "in_progress", "in-progress"}])
    resolved = len([item for item in complaints if item.get("status") == "resolved"])
    total = len(complaints)

    return [
        {"label": 'Total', "value": total, "trend": 'live', "color": 'text-theme-text'},
        {"label": 'Pending', "value": pending, "trend": 'live', "color": 'text-amber-500'},
        {"label": 'In Progress', "value": in_progress, "trend": 'live', "color": 'text-theme-accent'},
        {"label": 'Resolved', "value": resolved, "trend": 'live', "color": 'text-emerald-500'}
    ]

@router.get("/{complaint_id}")
def read_complaint(complaint_id: str, _admin=Depends(require_admin_user)):
    return get_complaint(complaint_id)

@router.post("")
def add_complaint(payload: ComplaintCreate, _admin=Depends(require_admin_user)):
    return create_complaint(payload.model_dump(exclude_none=True))

@router.put("/{complaint_id}")
def edit_complaint(complaint_id: str, payload: ComplaintUpdate, _admin=Depends(require_admin_user)):
    return update_complaint(complaint_id, payload.model_dump(exclude_none=True))

@router.delete("/{complaint_id}")
def remove_complaint(complaint_id: str, _admin=Depends(require_admin_user)):
    return delete_complaint(complaint_id)
