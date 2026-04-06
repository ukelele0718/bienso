from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from . import crud, crud_pretrained
from .db import get_db
from .schemas import (
    AccountOut,
    BarrierActionOut,
    ErrorOut,
    EventIn,
    EventOut,
    OcrRateOut,
    PretrainedImportIn,
    PretrainedJobOut,
    PretrainedJobsPageOut,
    PretrainedInferIn,
    RealtimeStatOut,
    TrafficStatOut,
    TransactionOut,
)

app = FastAPI(title="Vehicle LPR Backend", version="0.4.0")


@app.post("/api/v1/events", response_model=EventOut)
def create_event(payload: EventIn, db: Session = Depends(get_db)) -> EventOut:
    event, barrier_action = crud.create_event(db, payload.model_dump())
    plate_read = crud.get_event_plate_meta(db, event.id)

    return EventOut(
        id=event.id,
        camera_id=event.camera_id,
        timestamp=event.timestamp,
        direction=event.direction,
        vehicle_type=event.vehicle_type,
        track_id=event.track_id,
        plate_text=plate_read.plate_text if plate_read else None,
        confidence=plate_read.confidence if plate_read else None,
        snapshot_url=plate_read.snapshot_url if plate_read else None,
        registration_status=barrier_action.registration_status if barrier_action else None,
        barrier_action=barrier_action.barrier_action if barrier_action else None,
        barrier_reason=barrier_action.barrier_reason if barrier_action else None,
        needs_verification=barrier_action.needs_verification if barrier_action else None,
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
    result: List[EventOut] = []
    for e in events:
        plate_read = crud.get_event_plate_meta(db, e.id)
        barrier_action = crud.get_event_barrier_meta(db, e.id)
        result.append(
            EventOut(
                id=e.id,
                camera_id=e.camera_id,
                timestamp=e.timestamp,
                direction=e.direction,
                vehicle_type=e.vehicle_type,
                track_id=e.track_id,
                plate_text=plate_read.plate_text if plate_read else None,
                confidence=plate_read.confidence if plate_read else None,
                snapshot_url=plate_read.snapshot_url if plate_read else None,
                registration_status=barrier_action.registration_status if barrier_action else None,
                barrier_action=barrier_action.barrier_action if barrier_action else None,
                barrier_reason=barrier_action.barrier_reason if barrier_action else None,
                needs_verification=barrier_action.needs_verification if barrier_action else None,
            )
        )
    return result


@app.get("/api/v1/accounts/{plate_text}", response_model=AccountOut)
def get_account(plate_text: str, db: Session = Depends(get_db)) -> AccountOut:
    try:
        account = crud.get_account(db, plate_text)
    except crud.NotFoundError as exc:
        raise HTTPException(status_code=404, detail="account_not_found") from exc
    return AccountOut(
        plate_text=account.plate_text,
        balance_vnd=account.balance_vnd,
        registration_status=account.registration_status,
    )


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


@app.get("/api/v1/barrier-actions", response_model=List[BarrierActionOut])
def list_barrier_actions(plate: str = Query(...), db: Session = Depends(get_db)) -> List[BarrierActionOut]:
    rows = crud.list_barrier_actions_by_plate(db, plate)
    return [
        BarrierActionOut(
            id=row.id,
            event_id=row.event_id,
            plate_text=row.plate_text,
            registration_status=row.registration_status,
            barrier_action=row.barrier_action,
            barrier_reason=row.barrier_reason,
            needs_verification=row.needs_verification,
            verified_by=row.verified_by,
            verified_at=row.verified_at,
            created_at=row.created_at,
        )
        for row in rows
    ]


@app.post("/api/v1/barrier-actions/verify", response_model=BarrierActionOut)
def verify_barrier_action(plate: str, actor: str, db: Session = Depends(get_db)) -> BarrierActionOut:
    try:
        row = crud.verify_latest_hold(db, plate, actor)
    except crud.NotFoundError as exc:
        raise HTTPException(status_code=404, detail="barrier_action_not_found") from exc
    return BarrierActionOut(
        id=row.id,
        event_id=row.event_id,
        plate_text=row.plate_text,
        registration_status=row.registration_status,
        barrier_action=row.barrier_action,
        barrier_reason=row.barrier_reason,
        needs_verification=row.needs_verification,
        verified_by=row.verified_by,
        verified_at=row.verified_at,
        created_at=row.created_at,
    )


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
    return {"status": "ok", "time": datetime.utcnow().isoformat()}
