from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, BeforeValidator, Field

# Coerce UUID objects → str automatically in all schema fields typed as _Str.
# Needed because PostgreSQL uuid columns return Python UUID objects from SQLAlchemy,
# while our Pydantic models declare those fields as str.
_Str = Annotated[str, BeforeValidator(lambda v: str(v) if isinstance(v, UUID) else v)]

Direction = Literal["in", "out"]
VehicleType = Literal["motorbike", "car"]
OcrStatus = Literal["success", "partial", "failed"]
TransactionType = Literal["init", "event_charge", "manual_adjust"]
RegistrationStatus = Literal["registered", "temporary_registered", "unknown"]
BarrierActionType = Literal["open", "hold"]
AccountSortBy = Literal["created_at", "balance_vnd", "plate_text"]
SortOrder = Literal["asc", "desc"]
PretrainedJobType = Literal["infer", "import"]
PretrainedJobStatus = Literal["queued", "running", "success", "failed"]


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
    id: _Str
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
    id: _Str
    event_id: _Str
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
    id: _Str
    account_id: _Str
    event_id: _Str | None
    amount_vnd: int
    balance_after_vnd: int
    type: TransactionType
    created_at: datetime


class BarrierActionOut(BaseModel):
    id: _Str
    event_id: _Str
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
    sort_by: AccountSortBy = "created_at"
    sort_order: SortOrder = "desc"


class AccountsSummaryResponse(BaseModel):
    total_accounts: int
    registered_accounts: int
    temporary_registered_accounts: int


class ImportBatchOut(BaseModel):
    id: _Str
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
    transaction_id: _Str


class PretrainedInferIn(BaseModel):
    model_version: str = "mock-v1"
    source: str
    threshold: float | None = Field(default=None, ge=0.0, le=1.0)


class PretrainedImportItemIn(BaseModel):
    plate_text: str
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    vehicle_type: VehicleType | None = None
    event_time: datetime | None = None


class PretrainedImportIn(BaseModel):
    model_version: str = "mock-v1"
    source: str
    items: list[PretrainedImportItemIn] = Field(default_factory=list)


class PretrainedDetectionOut(BaseModel):
    id: _Str
    job_id: _Str
    plate_text: str | None = None
    confidence: float | None = None
    vehicle_type: VehicleType | None = None
    event_time: datetime | None = None
    metadata_json: dict | None = None
    created_at: datetime


class PretrainedJobOut(BaseModel):
    id: _Str
    job_type: PretrainedJobType
    status: PretrainedJobStatus
    model_version: str
    source: str
    threshold: float | None
    total_items: int
    processed_items: int
    created_at: datetime
    updated_at: datetime
    error_message: str | None = None
    result_preview: dict | None = None
    items: list[PretrainedDetectionOut] | None = None


class PretrainedJobsPageOut(BaseModel):
    items: list[PretrainedJobOut]
    page: int
    page_size: int
    total: int


class PretrainedJobsSummaryOut(BaseModel):
    total: int
    queued: int
    running: int
    success: int
    failed: int


class CameraOut(BaseModel):
    id: _Str
    name: str
    gate_type: str
    location: str | None = None
    stream_url: str | None = None
    is_active: bool
    created_at: datetime
