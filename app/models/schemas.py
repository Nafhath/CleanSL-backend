from datetime import date, datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field

UserRole = Literal["resident", "driver", "authority"]
ComplaintPriority = Literal["high", "medium", "low"]
ComplaintStatus = Literal["pending", "reviewed", "resolved", "rejected"]
TaskStatus = Literal["pending", "completed", "not_collected"]
DriverStatus = Literal["on_duty", "off_duty"]

class UserBase(BaseModel):
    id: str
    role: UserRole
    full_name: str
    phone_number: Optional[str] = None
    email: Optional[str] = None
    created_at: Optional[datetime] = None

class AddressBase(BaseModel):
    id: str
    resident_id: Optional[str] = None
    street_address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    zone_or_ward: Optional[str] = None
    last_collection_at: Optional[datetime] = None
    violation_count: int = 0


class AddressCreate(BaseModel):
    resident_id: Optional[str] = None
    street_address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    zone_or_ward: Optional[str] = None
    last_collection_at: Optional[datetime] = None
    violation_count: int = 0

class AddressUpdate(BaseModel):
    created_at: Optional[datetime] = None
    location_name: Optional[str] = None
    complaint_text: Optional[str] = None

class ComplaintBase(BaseModel):
    id: str
    resident_id: str
    address_id: Optional[str] = None
    photo_url: Optional[str] = None
    ai_sorted_percentage: Optional[int] = None
    priority_level: Optional[ComplaintPriority] = None
    status: ComplaintStatus = "pending"
    authority_notes: Optional[str] = None
    created_at: Optional[datetime] = None
    location_name: Optional[str] = None
    complaint_text: Optional[str] = None

class ComplaintCreate(BaseModel):
    resident_id: str
    address_id: Optional[str] = None
    photo_url: Optional[str] = None
    ai_sorted_percentage: Optional[int] = Field(default=None, ge=0, le=100)
    priority_level: Optional[ComplaintPriority] = None
    status: ComplaintStatus = "pending"
    authority_notes: Optional[str] = None
    location_name: Optional[str] = None
    complaint_text: Optional[str] = None


class ComplaintUpdate(BaseModel):
    photo_url: Optional[str] = None
    ai_sorted_percentage: Optional[int] = Field(default=None, ge=0, le=100)
    priority_level: Optional[ComplaintPriority] = None
    status: Optional[ComplaintStatus] = None
    authority_notes: Optional[str] = None
    location_name: Optional[str] = None
    complaint_text: Optional[str] = None


class CollectionTaskBase(BaseModel):
    id: str
    driver_id: str
    address_id: str
    scheduled_date: Optional[date] = None
    status: TaskStatus = "pending"
    voice_note_url: Optional[str] = None
    voice_transcript: Optional[str] = None
    updated_at: Optional[datetime] = None


class CollectionTaskCreate(BaseModel):
    driver_id: str
    address_id: str
    scheduled_date: Optional[date] = None
    status: TaskStatus = "pending"
    voice_note_url: Optional[str] = None
    voice_transcript: Optional[str] = None


class CollectionTaskUpdate(BaseModel):
    driver_id: Optional[str] = None
    address_id: Optional[str] = None
    scheduled_date: Optional[date] = None
    status: Optional[TaskStatus] = None
    voice_note_url: Optional[str] = None
    voice_transcript: Optional[str] = None


class DriverProfileUpdate(BaseModel):
    license_number: Optional[str] = None
    status: Optional[DriverStatus] = None


class DriverTrackingCreate(BaseModel):
    driver_id: str
    latitude: float
    longitude: float


class AnalyticsResponse(BaseModel):
    total_addresses: int
    total_complaints: int
    pending_complaints: int
    resolved_complaints: int
    total_tasks: int
    completed_tasks: int
    active_drivers: int