from __future__ import annotations

from app.services_pretrained import create_import_job, create_infer_job, get_job, list_jobs


def test_create_infer_job_has_success_status() -> None:
    row = create_infer_job(model_version="mock-v1", source="demo://frame-001.jpg", threshold=0.5)
    assert row["job_type"] == "infer"
    assert row["status"] == "success"
    assert row["processed_items"] == 1


def test_create_import_job_tracks_total_items() -> None:
    row = create_import_job(
        model_version="mock-v1",
        source="demo://batch-001",
        items=[
            {"plate_text": "51G12345", "confidence": 0.9},
            {"plate_text": "99X99999", "confidence": 0.8},
        ],
    )
    assert row["job_type"] == "import"
    assert row["total_items"] == 2
    assert row["processed_items"] == 2


def test_list_jobs_and_get_job_roundtrip() -> None:
    created = create_infer_job(model_version="mock-v1", source="demo://frame-xyz", threshold=None)
    items, total = list_jobs(page=1, page_size=50)
    assert total >= 1
    assert any(row["id"] == created["id"] for row in items)

    detail = get_job(created["id"])
    assert detail is not None
    assert detail["id"] == created["id"]
