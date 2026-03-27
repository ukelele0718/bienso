from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Direction = Literal["in", "out"]
VehicleType = Literal["motorbike", "car"]
OcrStatus = Literal["success", "partial", "failed"]
TransactionType = Literal["init", "event_charge", "manual_adjust"]


class EventIn(BaseModel):
    camera_id: str
    timestamp: datetime
    direction: Direction
    vehicle_type: VehicleType
    track_id: str
    plate_text: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    snapshot_url: str | None = None


class EventOut(EventIn):
    id: str


class EventQuery(BaseModel):
    plate: str | None = None
    from_time: datetime | None = None
    to_time: datetime | None = None
    direction: Direction | None = None
    vehicle_type: VehicleType | None = None


class PlateReadOut(BaseModel):
    id: str
    event_id: str
    plate_text: str | None
    confidence: float | None
    snapshot_url: str | None
    crop_url: str | None
    ocr_status: OcrStatus


class AccountOut(BaseModel):
    plate_text: str
    balance_vnd: int


class TransactionOut(BaseModel):
    id: str
    account_id: str
    event_id: str | None
    amount_vnd: int
    balance_after_vnd: int
    type: TransactionType
    created_at: datetime


class RealtimeStatOut(BaseModel):
    total_in: int
    total_out: int
    ocr_success_rate: float


class TrafficStatOut(BaseModel):
    bucket: str
    total_in: int
    total_out: int


class OcrRateOut(BaseModel):
    success_rate: float


class ErrorOut(BaseModel):
    detail: str
