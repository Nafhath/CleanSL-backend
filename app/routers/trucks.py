from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.trucks import create_truck_location_update, list_truck_dashboard_data

router = APIRouter(prefix="/trucks", tags=["Trucks"])

class LocationPayload(BaseModel):
    latitude: float
    longitude: float
    speed: float = 0.0
    driver_id: str | None = None
    location_name: str | None = None
    updated_at: str | None = None

@router.get("")
def read_trucks():
    return list_truck_dashboard_data()

@router.patch("/{truck_id}/location")
@router.post("/{truck_id}/location")
def update_truck_location(truck_id: str, payload: LocationPayload):
    try:
        data = create_truck_location_update(truck_id, payload.model_dump(exclude_none=True))
        return {"success": True, "message": f"Updated truck {truck_id} location", "data": data}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
