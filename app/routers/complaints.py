from fastapi import APIRouter, Query
from app.models.schemas import ComplaintCreate, ComplaintUpdate
from app.services.complaints import list_complaints, get_complaint, create_complaint, update_complaint, delete_complaint

router = APIRouter(prefix="/complaints", tags=["Complaints"])

@router.get("")
def read_complaints(
    status: str | None = Query(default=None),
    priority: str | None = Query(default=None)
):
    return list_complaints(status, priority)

@router.get("/stats/overview")
def read_complaints_stats():
    return [
        {"label": 'Total', "value": 124, "trend": '+12', "color": 'text-theme-text'},
        {"label": 'Pending', "value": 18, "trend": '-2', "color": 'text-amber-500'},
        {"label": 'In Progress', "value": 32, "trend": '+5', "color": 'text-theme-accent'},
        {"label": 'Resolved', "value": 74, "trend": '+24', "color": 'text-emerald-500'}
    ]

@router.get("/{complaint_id}")
def read_complaint(complaint_id: str):
    return get_complaint(complaint_id)

@router.post("")
def add_complaint(payload: ComplaintCreate):
    return create_complaint(payload.model_dump(exclude_none=True))

@router.put("/{complaint_id}")
def edit_complaint(complaint_id: str, payload: ComplaintUpdate):
    return update_complaint(complaint_id, payload.model_dump(exclude_none=True))

@router.delete("/{complaint_id}")
def remove_complaint(complaint_id: str):
    return delete_complaint(complaint_id)