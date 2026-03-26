from typing import Optional

from fastapi import APIRouter, File, Form, Query, UploadFile

from app.services.driver_reports import create_driver_report, list_driver_reports


router = APIRouter(prefix="/mobile", tags=["Mobile"])


@router.get("/health")
def read_mobile_health():
    return {"ok": True, "service": "mobile"}


@router.post("/driver/reports")
async def upload_driver_report(
    audio: UploadFile = File(...),
    driver_id: Optional[str] = Form(default=None),
    task_id: Optional[str] = Form(default=None),
    lane_name: Optional[str] = Form(default=None),
    house_number: Optional[int] = Form(default=None),
    transcription: Optional[str] = Form(default=None),
):
    file_bytes = await audio.read()
    return create_driver_report(
        file_bytes=file_bytes,
        filename=audio.filename,
        driver_id=driver_id,
        task_id=task_id,
        lane_name=lane_name,
        house_number=house_number,
        transcription=transcription,
    )


@router.get("/driver/reports")
def read_driver_reports(
    driver_id: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
):
    return list_driver_reports(driver_id=driver_id, limit=limit)
