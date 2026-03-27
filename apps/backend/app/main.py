from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from . import crud
from .db import get_db
from .schemas import (
    AccountOut,
    ErrorOut,
    EventIn,
    EventOut,
    OcrRateOut,
    RealtimeStatOut,
    TrafficStatOut,
    TransactionOut,
)

app = FastAPI(title="Vehicle LPR Backend", version="0.3.0")


@app.post("/api/v1/events", response_model=EventOut)
def create_event(payload: EventIn, db: Session = Depends(get_db)) -> EventOut:
    event = crud.create_event(db, payload.model_dump())
    plate_text = payload.plate_text
    confidence = payload.confidence
    snapshot_url = payload.snapshot_url
    return EventOut(
        id=event.id,
        camera_id=event.camera_id,
        timestamp=event.timestamp,
        direction=event.direction,
        vehicle_type=event.vehicle_type,
        track_id=event.track_id,
        plate_text=plate_text,
        confidence=confidence,
        snapshot_url=snapshot_url,
    )


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
    return [
        EventOut(
            id=e.id,
            camera_id=e.camera_id,
            timestamp=e.timestamp,
            direction=e.direction,
            vehicle_type=e.vehicle_type,
            track_id=e.track_id,
            plate_text=None,
            confidence=None,
            snapshot_url=None,
        )
        for e in events
    ]


@app.get("/api/v1/accounts/{plate_text}", response_model=AccountOut)
def get_account(plate_text: str, db: Session = Depends(get_db)) -> AccountOut:
    try:
        account = crud.get_account(db, plate_text)
    except crud.NotFoundError as exc:
        raise HTTPException(status_code=404, detail="account_not_found") from exc
    return AccountOut(plate_text=account.plate_text, balance_vnd=account.balance_vnd)


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
