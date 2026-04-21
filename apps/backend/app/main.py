from __future__ import annotations

# mypy: disable-error-code="arg-type,misc"
# Reason: SQLAlchemy Mapped[str] -> Pydantic Literal[...] + dict -> Pydantic model;
# validated at runtime by Pydantic.

import os
from datetime import UTC, datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import crud, crud_pretrained
from .response_mappers import to_account_out, to_barrier_action_out, to_event_out
from .db import get_db
from .schemas import (
    AccountListItem,
    AccountListResponse,
    AccountOut,
    AccountsSummaryResponse,
    ApiErrorOut,
    AdjustBalanceIn,
    AdjustBalanceResponse,
    BarrierActionOut,
    ErrorOut,
    EventIn,
    EventOut,
    ImportBatchesSummaryResponse,
    ImportBatchOut,
    MarkRegisteredResponse,
    OcrRateOut,
    AccountSortBy,
    SortOrder,
    PretrainedImportIn,
    PretrainedJobOut,
    PretrainedJobsPageOut,
    PretrainedJobsSummaryOut,
    PretrainedInferIn,
    RealtimeStatOut,
    TrafficStatOut,
    TransactionOut,
)

app = FastAPI(title="Vehicle LPR Backend", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _auto_create_tables() -> None:
    """Auto-create tables when using SQLite (dev/demo mode)."""
    from .db import Base, engine  # noqa: WPS433
    from . import models  # noqa: F401, WPS433 — ensure models registered

    if "sqlite" in str(engine.url):
        Base.metadata.create_all(bind=engine)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else "http_error"
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": detail,
            "message": detail.replace("_", " "),
            "details": None,
        },
    )


@app.post(
    "/api/v1/events",
    response_model=EventOut,
    responses={400: {"model": ApiErrorOut}, 404: {"model": ApiErrorOut}},
)
def create_event(payload: EventIn, db: Session = Depends(get_db)) -> EventOut:
    event, barrier_action = crud.create_event(db, payload.model_dump())
    plate_read = crud.get_event_plate_meta(db, event.id)

    return to_event_out(event, plate_read, barrier_action)


@app.get("/api/v1/events", response_model=List[EventOut])
def list_events(
    plate: str | None = Query(default=None),
    from_time: datetime | None = Query(default=None),
    to_time: datetime | None = Query(default=None),
    direction: str | None = Query(default=None),
    vehicle_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> List[EventOut]:
    events = crud.list_events(db, plate, from_time, to_time, direction, vehicle_type)
    result: List[EventOut] = []
    for e in events:
        plate_read = crud.get_event_plate_meta(db, e.id)
        barrier_action = crud.get_event_barrier_meta(db, e.id)
        result.append(to_event_out(e, plate_read, barrier_action))
    return result


@app.get(
    "/api/v1/accounts",
    response_model=AccountListResponse,
    responses={
        200: {
            "description": "List accounts with filters and sorting",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "plate_text": "51G12345",
                                "balance_vnd": 47000,
                                "registration_status": "registered",
                            }
                        ],
                        "total": 123,
                        "page": 1,
                        "page_size": 20,
                        "sort_by": "created_at",
                        "sort_order": "desc",
                    }
                }
            },
        },
        400: {"model": ApiErrorOut},
    },
)
def list_accounts(
    plate: str | None = Query(default=None),
    registration_status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: AccountSortBy = Query(default="created_at"),
    sort_order: SortOrder = Query(default="desc"),
    db: Session = Depends(get_db),
) -> AccountListResponse:
    accounts, total = crud.list_accounts(
        db,
        plate,
        registration_status,
        page,
        page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return AccountListResponse(
        items=[
            AccountListItem(
                plate_text=acc.plate_text,
                balance_vnd=acc.balance_vnd,
                registration_status=acc.registration_status,
            )
            for acc in accounts
        ],
        total=total,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@app.get("/api/v1/accounts/summary", response_model=AccountsSummaryResponse)
def get_accounts_summary(db: Session = Depends(get_db)) -> AccountsSummaryResponse:
    summary = crud.get_accounts_summary(db)
    return AccountsSummaryResponse(**summary)


@app.get("/api/v1/import-batches", response_model=List[ImportBatchOut])
def get_import_batches(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> List[ImportBatchOut]:
    rows = crud.list_import_batches(db, limit=limit)
    return [
        ImportBatchOut(
            id=str(row.id),
            source=row.source,
            seed_group=row.seed_group,
            imported_count=row.imported_count,
            skipped_count=row.skipped_count,
            invalid_count=row.invalid_count,
            created_at=row.created_at,
        )
        for row in rows
    ]


@app.get("/api/v1/import-batches/summary", response_model=ImportBatchesSummaryResponse)
def get_import_batches_summary(db: Session = Depends(get_db)) -> ImportBatchesSummaryResponse:
    summary = crud.get_import_batches_summary(db)
    return ImportBatchesSummaryResponse(**summary)


@app.get("/api/v1/accounts/{plate_text}", response_model=AccountOut)
def get_account(plate_text: str, db: Session = Depends(get_db)) -> AccountOut:
    try:
        account = crud.get_account(db, plate_text)
    except crud.NotFoundError as exc:
        raise HTTPException(status_code=404, detail="account_not_found") from exc
    return to_account_out(account)


@app.get("/api/v1/accounts/{plate_text}/transactions", response_model=List[TransactionOut])
def list_transactions(plate_text: str, db: Session = Depends(get_db)) -> List[TransactionOut]:
    try:
        account = crud.get_account(db, plate_text)
    except crud.NotFoundError as exc:
        raise HTTPException(status_code=404, detail="account_not_found") from exc
    txs = crud.list_transactions(db, account.id)
    return [
        TransactionOut(
            id=str(t.id),
            account_id=str(t.account_id),
            event_id=str(t.event_id) if t.event_id else None,
            amount_vnd=t.amount_vnd,
            balance_after_vnd=t.balance_after_vnd,
            type=t.type,
            created_at=t.created_at,
        )
        for t in txs
    ]


@app.post("/api/v1/accounts/{plate_text}/mark-registered", response_model=MarkRegisteredResponse)
def mark_registered(plate_text: str, db: Session = Depends(get_db)) -> MarkRegisteredResponse:
    try:
        account = crud.mark_account_registered(db, plate_text)
    except crud.NotFoundError as exc:
        raise HTTPException(status_code=404, detail="account_not_found") from exc
    return MarkRegisteredResponse(
        plate_text=account.plate_text,
        registration_status=account.registration_status,
    )


@app.post("/api/v1/accounts/{plate_text}/adjust-balance", response_model=AdjustBalanceResponse)
def adjust_balance(
    plate_text: str,
    payload: AdjustBalanceIn,
    db: Session = Depends(get_db),
) -> AdjustBalanceResponse:
    try:
        account, tx = crud.adjust_account_balance(
            db,
            plate_text,
            payload.amount_vnd,
            actor=payload.actor,
            reason=payload.reason,
        )
    except crud.NotFoundError as exc:
        raise HTTPException(status_code=404, detail="account_not_found") from exc
    return AdjustBalanceResponse(
        plate_text=account.plate_text,
        balance_vnd=account.balance_vnd,
        delta_vnd=payload.amount_vnd,
        transaction_id=tx.id,
    )


@app.get("/api/v1/barrier-actions", response_model=List[BarrierActionOut])
def list_barrier_actions(plate: str | None = Query(default=None), db: Session = Depends(get_db)) -> List[BarrierActionOut]:
    rows = crud.list_barrier_actions(db, plate)
    return [to_barrier_action_out(row) for row in rows]


@app.post(
    "/api/v1/barrier-actions/verify",
    response_model=BarrierActionOut,
    responses={
        200: {
            "description": "Verify latest hold action for a plate",
            "content": {
                "application/json": {
                    "example": {
                        "id": "uuid",
                        "event_id": "uuid",
                        "plate_text": "51G12345",
                        "registration_status": "temporary_registered",
                        "barrier_action": "open",
                        "barrier_reason": "manual_verify_open",
                        "needs_verification": False,
                        "verified_by": "dashboard_operator",
                        "verified_at": "2026-04-10T10:00:00Z",
                        "created_at": "2026-04-10T09:59:00Z",
                    }
                }
            },
        },
        404: {"model": ApiErrorOut},
    },
)
def verify_barrier_action(plate: str, actor: str, db: Session = Depends(get_db)) -> BarrierActionOut:
    try:
        row = crud.verify_latest_hold(db, plate, actor)
    except crud.NotFoundError as exc:
        raise HTTPException(status_code=404, detail="barrier_action_not_found") from exc
    return to_barrier_action_out(row)


@app.get("/api/v1/stats/realtime", response_model=RealtimeStatOut)
def get_realtime_stats(db: Session = Depends(get_db)) -> RealtimeStatOut:
    stats = crud.get_realtime_stats(db)
    return RealtimeStatOut(**stats)


@app.get("/api/v1/stats/traffic", response_model=List[TrafficStatOut])
def get_traffic_stats(group_by: str = "hour", db: Session = Depends(get_db)) -> List[TrafficStatOut]:
    rows = crud.get_traffic_stats(db, group_by)
    return [TrafficStatOut(**row) for row in rows]


@app.get("/api/v1/stats/ocr-success-rate", response_model=OcrRateOut)
def get_ocr_success_rate(db: Session = Depends(get_db)) -> OcrRateOut:
    success_rate = crud.get_ocr_rate(db)
    return OcrRateOut(success_rate=success_rate)


@app.get("/api/v1/errors/sample", response_model=ErrorOut)
def get_error_sample() -> ErrorOut:
    return ErrorOut(detail="not_implemented")


@app.post("/api/v1/pretrained/infer", response_model=PretrainedJobOut)
def create_pretrained_infer_job(payload: PretrainedInferIn, db: Session = Depends(get_db)) -> PretrainedJobOut:
    row = crud_pretrained.create_job(
        db,
        job_type="infer",
        model_version=payload.model_version,
        source=payload.source,
        threshold=payload.threshold,
        total_items=1,
        processed_items=1,
        status="success",
        result_preview={
            "plate_text": "MOCK12345",
            "confidence": 0.92,
            "vehicle_type": "motorbike",
        },
    )
    db.commit()
    db.refresh(row)
    return PretrainedJobOut(**row.__dict__)


@app.post("/api/v1/pretrained/import", response_model=PretrainedJobOut)
def create_pretrained_import_job(payload: PretrainedImportIn, db: Session = Depends(get_db)) -> PretrainedJobOut:
    items = [item.model_dump() for item in payload.items]
    row = crud_pretrained.create_job(
        db,
        job_type="import",
        model_version=payload.model_version,
        source=payload.source,
        threshold=None,
        total_items=len(items),
        processed_items=len(items),
        status="success",
        result_preview={
            "imported": len(items),
            "skipped": 0,
            "invalid": 0,
        },
    )
    detections = crud_pretrained.create_detections(db, job_id=row.id, items=items)
    db.commit()
    db.refresh(row)
    return PretrainedJobOut(
        id=row.id,
        job_type=row.job_type,
        status=row.status,
        model_version=row.model_version,
        source=row.source,
        threshold=row.threshold,
        total_items=row.total_items,
        processed_items=row.processed_items,
        created_at=row.created_at,
        updated_at=row.updated_at,
        error_message=row.error_message,
        result_preview=row.result_preview_json,
        items=[
            {
                "id": d.id,
                "job_id": d.job_id,
                "plate_text": d.plate_text,
                "confidence": d.confidence,
                "vehicle_type": d.vehicle_type,
                "event_time": d.event_time,
                "metadata_json": d.metadata_json,
                "created_at": d.created_at,
            }
            for d in detections
        ],
    )


@app.get("/api/v1/pretrained/jobs", response_model=PretrainedJobsPageOut)
def list_pretrained_jobs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PretrainedJobsPageOut:
    rows, total = crud_pretrained.list_jobs(db, page=page, page_size=page_size)
    return PretrainedJobsPageOut(
        items=[
            PretrainedJobOut(
                id=row.id,
                job_type=row.job_type,
                status=row.status,
                model_version=row.model_version,
                source=row.source,
                threshold=row.threshold,
                total_items=row.total_items,
                processed_items=row.processed_items,
                created_at=row.created_at,
                updated_at=row.updated_at,
                error_message=row.error_message,
                result_preview=row.result_preview_json,
            )
            for row in rows
        ],
        page=page,
        page_size=page_size,
        total=total,
    )


@app.get("/api/v1/pretrained/jobs/summary", response_model=PretrainedJobsSummaryOut)
def get_pretrained_jobs_summary(db: Session = Depends(get_db)) -> PretrainedJobsSummaryOut:
    return PretrainedJobsSummaryOut(**crud_pretrained.get_jobs_summary(db))


@app.get("/api/v1/pretrained/jobs/{job_id}", response_model=PretrainedJobOut)
def get_pretrained_job(job_id: str, db: Session = Depends(get_db)) -> PretrainedJobOut:
    row = crud_pretrained.get_job(db, job_id)
    if row is None:
        raise HTTPException(status_code=404, detail="pretrained_job_not_found")
    detections = crud_pretrained.list_detections_by_job(db, row.id)
    return PretrainedJobOut(
        id=row.id,
        job_type=row.job_type,
        status=row.status,
        model_version=row.model_version,
        source=row.source,
        threshold=row.threshold,
        total_items=row.total_items,
        processed_items=row.processed_items,
        created_at=row.created_at,
        updated_at=row.updated_at,
        error_message=row.error_message,
        result_preview=row.result_preview_json,
        items=[
            {
                "id": d.id,
                "job_id": d.job_id,
                "plate_text": d.plate_text,
                "confidence": d.confidence,
                "vehicle_type": d.vehicle_type,
                "event_time": d.event_time,
                "metadata_json": d.metadata_json,
                "created_at": d.created_at,
            }
            for d in detections
        ],
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "time": datetime.now(UTC).isoformat()}


# Static files — must be mounted after all API routes to avoid path conflicts
_snapshots_dir = os.environ.get("SNAPSHOT_DIR", "snapshots")
if os.path.isdir(_snapshots_dir):
    app.mount("/static/snapshots", StaticFiles(directory=_snapshots_dir), name="snapshots")
