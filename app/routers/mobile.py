from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from pydantic import BaseModel

from app.core.auth import require_admin_user
from app.services.driver_reports import (
    create_driver_report,
    list_driver_reports,
    update_driver_report_status,
)


router = APIRouter(prefix="/mobile", tags=["Mobile"])


class DriverReportStatusPayload(BaseModel):
    status: str


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
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
):
    return list_driver_reports(driver_id=driver_id, status=status, limit=limit)


@router.get("/admin/driver-reports")
def read_admin_driver_reports(
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    _admin=Depends(require_admin_user),
):
    return list_driver_reports(status=status, limit=limit)


@router.patch("/admin/driver-reports/{report_id}")
def patch_driver_report_status(
    report_id: str,
    payload: DriverReportStatusPayload,
    _admin=Depends(require_admin_user),
):
    return update_driver_report_status(report_id=report_id, status_value=payload.status)
