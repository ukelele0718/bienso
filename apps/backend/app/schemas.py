from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Direction = Literal["in", "out"]
VehicleType = Literal["motorbike", "car"]
OcrStatus = Literal["success", "partial", "failed"]
TransactionType = Literal["init", "event_charge", "manual_adjust"]
RegistrationStatus = Literal["registered", "temporary_registered", "unknown"]
BarrierActionType = Literal["open", "hold"]


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
    registration_status: RegistrationStatus | None = None
    barrier_action: BarrierActionType | None = None
    barrier_reason: str | None = None
    needs_verification: bool | None = None


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
    registration_status: RegistrationStatus | None = None


class TransactionOut(BaseModel):
    id: str
    account_id: str
    event_id: str | None
    amount_vnd: int
    balance_after_vnd: int
    type: TransactionType
    created_at: datetime


class BarrierActionOut(BaseModel):
    id: str
    event_id: str
    plate_text: str | None
    registration_status: RegistrationStatus
    barrier_action: BarrierActionType
    barrier_reason: str
    needs_verification: bool
    verified_by: str | None
    verified_at: datetime | None
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


class ApiErrorOut(BaseModel):
    code: str
    message: str
    details: dict | None = None


class AccountListItem(BaseModel):
    plate_text: str
    balance_vnd: int
    registration_status: RegistrationStatus | None = None


class AccountListResponse(BaseModel):
    items: list[AccountListItem]
    total: int
    page: int
    page_size: int


class AccountsSummaryResponse(BaseModel):
    total_accounts: int
    registered_accounts: int
    temporary_registered_accounts: int


class ImportBatchOut(BaseModel):
    id: str
    source: str
    seed_group: str | None = None
    imported_count: int
    skipped_count: int
    invalid_count: int
    created_at: datetime


class ImportBatchesSummaryResponse(BaseModel):
    total_batches: int
    total_imported: int
    total_skipped: int
    total_invalid: int


class MarkRegisteredResponse(BaseModel):
    plate_text: str
    registration_status: RegistrationStatus


class AdjustBalanceIn(BaseModel):
    amount_vnd: int
    actor: str | None = None
    reason: str | None = None


class AdjustBalanceResponse(BaseModel):
    plate_text: str
    balance_vnd: int
    delta_vnd: int
    transaction_id: str
