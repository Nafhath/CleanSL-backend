from fastapi import APIRouter, Depends
from app.core.auth import require_admin_user
from app.models.schemas import DriverProfileUpdate, DriverTrackingCreate
from app.services.drivers import (
    list_drivers,
    update_driver_profile,
    create_driver_tracking,
    get_driver_latest_location,
)

router = APIRouter(prefix="/drivers", tags=["Drivers"])


@router.get("")
def read_drivers(_admin=Depends(require_admin_user)):
    return list_drivers()


@router.put("/{driver_id}/profile")
def edit_driver_profile(driver_id: str, payload: DriverProfileUpdate, _admin=Depends(require_admin_user)):
    return update_driver_profile(driver_id, payload.model_dump(exclude_none=True))


@router.post("/tracking")
def add_driver_tracking(payload: DriverTrackingCreate, _admin=Depends(require_admin_user)):
    return create_driver_tracking(payload.model_dump())


@router.get("/{driver_id}/latest-location")
def read_driver_latest_location(driver_id: str, _admin=Depends(require_admin_user)):
    return get_driver_latest_location(driver_id)
