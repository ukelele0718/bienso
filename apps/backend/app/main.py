from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from . import crud
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
    RealtimeStatOut,
    TrafficStatOut,
    TransactionOut,
)

app = FastAPI(title="Vehicle LPR Backend", version="0.4.0")


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


@app.get("/api/v1/accounts", response_model=AccountListResponse)
def list_accounts(
    plate: str | None = Query(default=None),
    registration_status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> AccountListResponse:
    accounts, total = crud.list_accounts(db, plate, registration_status, page, page_size)
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
            id=row.id,
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
            id=t.id,
            account_id=t.account_id,
            event_id=t.event_id,
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


@app.post("/api/v1/barrier-actions/verify", response_model=BarrierActionOut)
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


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "time": datetime.utcnow().isoformat()}
