from fastapi import APIRouter
from app.models.schemas import DriverProfileUpdate, DriverTrackingCreate
from app.services.drivers import (
    list_drivers,
    update_driver_profile,
    create_driver_tracking,
    get_driver_latest_location,
)

router = APIRouter(prefix="/drivers", tags=["Drivers"])


@router.get("")
def read_drivers():
    return list_drivers()


@router.put("/{driver_id}/profile")
def edit_driver_profile(driver_id: str, payload: DriverProfileUpdate):
    return update_driver_profile(driver_id, payload.model_dump(exclude_none=True))


@router.post("/tracking")
def add_driver_tracking(payload: DriverTrackingCreate):
    return create_driver_tracking(payload.model_dump())


@router.get("/{driver_id}/latest-location")
def read_driver_latest_location(driver_id: str):
    return get_driver_latest_location(driver_id)