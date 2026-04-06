from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


_PRETRAINED_JOBS: dict[str, dict[str, Any]] = {}


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def create_infer_job(model_version: str, source: str, threshold: float | None = None) -> dict[str, Any]:
    job_id = str(uuid4())
    job = {
        "id": job_id,
        "job_type": "infer",
        "status": "success",
        "model_version": model_version,
        "source": source,
        "threshold": threshold,
        "total_items": 1,
        "processed_items": 1,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "error_message": None,
        "result_preview": {
            "plate_text": "MOCK12345",
            "confidence": 0.92,
            "vehicle_type": "motorbike",
        },
    }
    _PRETRAINED_JOBS[job_id] = job
    return job


def create_import_job(model_version: str, source: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    job_id = str(uuid4())
    total = len(items)
    job = {
        "id": job_id,
        "job_type": "import",
        "status": "success",
        "model_version": model_version,
        "source": source,
        "threshold": None,
        "total_items": total,
        "processed_items": total,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "error_message": None,
        "result_preview": {
            "imported": total,
            "skipped": 0,
            "invalid": 0,
        },
    }
    _PRETRAINED_JOBS[job_id] = job
    return job


def list_jobs(page: int = 1, page_size: int = 20) -> tuple[list[dict[str, Any]], int]:
    rows = sorted(_PRETRAINED_JOBS.values(), key=lambda x: x["created_at"], reverse=True)
    total = len(rows)
    start = (page - 1) * page_size
    end = start + page_size
    return rows[start:end], total


def get_job(job_id: str) -> dict[str, Any] | None:
    return _PRETRAINED_JOBS.get(job_id)
