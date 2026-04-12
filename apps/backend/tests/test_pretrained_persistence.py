"""Persistence tests for crud_pretrained (real DB via test fixture)."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app import crud_pretrained
from app.models import PretrainedDetection, PretrainedJob


class TestCreateJob:
    """Test crud_pretrained.create_job persists correctly."""

    def test_create_infer_job_persists(self, db_session: Session) -> None:
        row = crud_pretrained.create_job(
            db_session,
            job_type="infer",
            model_version="test-v1",
            source="demo://frame.jpg",
            threshold=0.5,
            total_items=1,
            processed_items=1,
            status="success",
        )
        db_session.commit()

        fetched = db_session.query(PretrainedJob).filter_by(id=row.id).first()
        assert fetched is not None
        assert fetched.job_type == "infer"
        assert fetched.status == "success"
        assert fetched.model_version == "test-v1"
        assert fetched.total_items == 1

    def test_create_import_job_persists(self, db_session: Session) -> None:
        row = crud_pretrained.create_job(
            db_session,
            job_type="import",
            model_version="test-v1",
            source="demo://batch",
            threshold=None,
            total_items=5,
            processed_items=5,
            status="success",
        )
        db_session.commit()

        fetched = db_session.query(PretrainedJob).filter_by(id=row.id).first()
        assert fetched is not None
        assert fetched.job_type == "import"
        assert fetched.total_items == 5

    def test_create_failed_job(self, db_session: Session) -> None:
        row = crud_pretrained.create_job(
            db_session,
            job_type="infer",
            model_version="test-v1",
            source="demo://bad.jpg",
            threshold=None,
            total_items=1,
            processed_items=0,
            status="failed",
            error_message="Model load error",
        )
        db_session.commit()

        fetched = db_session.query(PretrainedJob).filter_by(id=row.id).first()
        assert fetched is not None
        assert fetched.status == "failed"
        assert fetched.error_message == "Model load error"


class TestCreateDetections:
    """Test crud_pretrained.create_detections batch insert."""

    def test_batch_insert_detections(self, db_session: Session) -> None:
        job = crud_pretrained.create_job(
            db_session,
            job_type="import",
            model_version="test-v1",
            source="demo://batch",
            threshold=None,
            total_items=3,
            processed_items=3,
        )
        items = [
            {"plate_text": "29A12345", "confidence": 0.95, "vehicle_type": "motorbike"},
            {"plate_text": "51G67890", "confidence": 0.88, "vehicle_type": "car"},
            {"plate_text": None, "confidence": 0.3},
        ]
        detections = crud_pretrained.create_detections(db_session, job_id=job.id, items=items)
        db_session.commit()

        assert len(detections) == 3
        stored = db_session.query(PretrainedDetection).filter_by(job_id=job.id).all()
        assert len(stored) == 3

    def test_empty_batch(self, db_session: Session) -> None:
        job = crud_pretrained.create_job(
            db_session,
            job_type="import",
            model_version="test-v1",
            source="demo://empty",
            threshold=None,
            total_items=0,
            processed_items=0,
        )
        detections = crud_pretrained.create_detections(db_session, job_id=job.id, items=[])
        db_session.commit()

        assert len(detections) == 0


class TestListAndGetJobs:
    """Test list_jobs, get_job, list_detections_by_job."""

    def test_list_jobs_pagination(self, db_session: Session) -> None:
        for i in range(5):
            crud_pretrained.create_job(
                db_session,
                job_type="infer",
                model_version="test-v1",
                source=f"demo://frame-{i}.jpg",
                threshold=None,
                total_items=1,
                processed_items=1,
            )
        db_session.commit()

        rows, total = crud_pretrained.list_jobs(db_session, page=1, page_size=3)
        assert len(rows) == 3
        assert total >= 5

    def test_get_job_found(self, db_session: Session) -> None:
        job = crud_pretrained.create_job(
            db_session,
            job_type="infer",
            model_version="test-v1",
            source="demo://find-me.jpg",
            threshold=0.7,
            total_items=1,
            processed_items=1,
        )
        db_session.commit()

        fetched = crud_pretrained.get_job(db_session, job.id)
        assert fetched is not None
        assert fetched.id == job.id

    def test_get_job_not_found(self, db_session: Session) -> None:
        fetched = crud_pretrained.get_job(db_session, "nonexistent-id")
        assert fetched is None

    def test_list_detections_by_job(self, db_session: Session) -> None:
        job = crud_pretrained.create_job(
            db_session,
            job_type="import",
            model_version="test-v1",
            source="demo://det-test",
            threshold=None,
            total_items=2,
            processed_items=2,
        )
        crud_pretrained.create_detections(
            db_session,
            job_id=job.id,
            items=[
                {"plate_text": "AAA111", "confidence": 0.9},
                {"plate_text": "BBB222", "confidence": 0.8},
            ],
        )
        db_session.commit()

        dets = crud_pretrained.list_detections_by_job(db_session, job.id)
        assert len(dets) == 2


class TestJobsSummary:
    """Test get_jobs_summary counts."""

    def test_summary_counts(self, db_session: Session) -> None:
        for status in ["success", "success", "failed", "queued"]:
            crud_pretrained.create_job(
                db_session,
                job_type="infer",
                model_version="test-v1",
                source="demo://summary",
                threshold=None,
                total_items=1,
                processed_items=1 if status == "success" else 0,
                status=status,
            )
        db_session.commit()

        summary = crud_pretrained.get_jobs_summary(db_session)
        assert summary["total"] >= 4
        assert summary["success"] >= 2
        assert summary["failed"] >= 1
        assert summary["queued"] >= 1
