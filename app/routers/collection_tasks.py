from fastapi import APIRouter, Depends, Query
from app.core.auth import require_admin_user
from app.models.schemas import CollectionTaskCreate, CollectionTaskUpdate
from app.services.collection_tasks import list_tasks, get_task, create_task, update_task, delete_task

router = APIRouter(prefix="/tasks", tags=["Collection Tasks"])


@router.get("")
def read_tasks(
    status: str | None = Query(default=None),
    driver_id: str | None = Query(default=None),
    _admin=Depends(require_admin_user)
):
    return list_tasks(status, driver_id)


@router.get("/{task_id}")
def read_task(task_id: str, _admin=Depends(require_admin_user)):
    return get_task(task_id)


@router.post("")
def add_task(payload: CollectionTaskCreate, _admin=Depends(require_admin_user)):
    return create_task(payload.model_dump(exclude_none=True))


@router.put("/{task_id}")
def edit_task(task_id: str, payload: CollectionTaskUpdate, _admin=Depends(require_admin_user)):
    return update_task(task_id, payload.model_dump(exclude_none=True))


@router.delete("/{task_id}")
def remove_task(task_id: str, _admin=Depends(require_admin_user)):
    return delete_task(task_id)
