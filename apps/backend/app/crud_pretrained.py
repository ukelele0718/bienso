from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from .models import PretrainedDetection, PretrainedJob


def create_job(
    db: Session,
    *,
    job_type: str,
    model_version: str,
    source: str,
    threshold: float | None,
    total_items: int,
    processed_items: int,
    status: str = "success",
    error_message: str | None = None,
    result_preview: dict | None = None,
) -> PretrainedJob:
    now = datetime.now(UTC)
    row = PretrainedJob(
        id=str(uuid4()),
        job_type=job_type,
        status=status,
        model_version=model_version,
        source=source,
        threshold=threshold,
        total_items=total_items,
        processed_items=processed_items,
        error_message=error_message,
        result_preview_json=result_preview,
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    db.flush()
    return row


def create_detections(db: Session, *, job_id: str, items: list[dict[str, Any]]) -> list[PretrainedDetection]:
    rows: list[PretrainedDetection] = []
    now = datetime.now(UTC)
    for item in items:
        row = PretrainedDetection(
            id=str(uuid4()),
            job_id=job_id,
            plate_text=item.get("plate_text"),
            confidence=item.get("confidence"),
            vehicle_type=item.get("vehicle_type"),
            event_time=item.get("event_time"),
            metadata_json=item.get("metadata_json"),
            created_at=now,
        )
        db.add(row)
        rows.append(row)
    db.flush()
    return rows


def list_jobs(db: Session, *, page: int = 1, page_size: int = 20) -> tuple[list[PretrainedJob], int]:
    stmt = select(PretrainedJob).order_by(PretrainedJob.created_at.desc())
    total = db.execute(select(func.count()).select_from(PretrainedJob)).scalar_one()
    rows = list(
        db.execute(stmt.offset((page - 1) * page_size).limit(page_size)).scalars().all()
    )
    return rows, int(total)


def get_job(db: Session, job_id: str) -> PretrainedJob | None:
    return db.execute(select(PretrainedJob).where(PretrainedJob.id == job_id)).scalar_one_or_none()


def list_detections_by_job(db: Session, job_id: str) -> list[PretrainedDetection]:
    return list(
        db.execute(
            select(PretrainedDetection)
            .where(PretrainedDetection.job_id == job_id)
            .order_by(PretrainedDetection.created_at.asc())
        )
        .scalars()
        .all()
    )


def get_jobs_summary(db: Session) -> dict[str, int]:
    row = db.execute(
        select(
            func.count().label("total"),
            func.sum(case((PretrainedJob.status == "queued", 1), else_=0)).label("queued"),
            func.sum(case((PretrainedJob.status == "running", 1), else_=0)).label("running"),
            func.sum(case((PretrainedJob.status == "success", 1), else_=0)).label("success"),
            func.sum(case((PretrainedJob.status == "failed", 1), else_=0)).label("failed"),
        )
        .select_from(PretrainedJob)
    ).one()

    return {
        "total": int(row.total or 0),
        "queued": int(row.queued or 0),
        "running": int(row.running or 0),
        "success": int(row.success or 0),
        "failed": int(row.failed or 0),
    }
