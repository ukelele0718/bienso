"""API contract tests for pretrained endpoints."""
from __future__ import annotations

from fastapi.testclient import TestClient


class TestPretrainedInferEndpoint:
    """POST /api/v1/pretrained/infer"""

    def test_infer_returns_200(self, client: TestClient) -> None:
        res = client.post(
            "/api/v1/pretrained/infer",
            json={"source": "demo://frame.jpg", "model_version": "mock-v1", "threshold": 0.5},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["job_type"] == "infer"
        assert body["status"] == "success"
        assert "id" in body
        assert "created_at" in body

    def test_infer_rejects_missing_source(self, client: TestClient) -> None:
        res = client.post("/api/v1/pretrained/infer", json={"model_version": "mock-v1"})
        assert res.status_code == 422

    def test_infer_rejects_invalid_threshold(self, client: TestClient) -> None:
        res = client.post(
            "/api/v1/pretrained/infer",
            json={"source": "demo://x.jpg", "threshold": 1.5},
        )
        assert res.status_code == 422


class TestPretrainedImportEndpoint:
    """POST /api/v1/pretrained/import"""

    def test_import_creates_job(self, client: TestClient) -> None:
        res = client.post(
            "/api/v1/pretrained/import",
            json={
                "source": "demo://batch",
                "model_version": "mock-v1",
                "items": [
                    {"plate_text": "29A12345", "confidence": 0.9},
                    {"plate_text": "51G67890", "confidence": 0.8},
                ],
            },
        )
        assert res.status_code == 200
        body = res.json()
        assert body["job_type"] == "import"
        assert body["total_items"] == 2
        assert body["processed_items"] == 2

    def test_import_empty_items(self, client: TestClient) -> None:
        res = client.post(
            "/api/v1/pretrained/import",
            json={"source": "demo://empty", "model_version": "mock-v1", "items": []},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["total_items"] == 0


class TestPretrainedJobsListEndpoint:
    """GET /api/v1/pretrained/jobs"""

    def test_list_returns_paginated_response(self, client: TestClient) -> None:
        # Create a job first
        client.post(
            "/api/v1/pretrained/infer",
            json={"source": "demo://list-test.jpg", "model_version": "mock-v1"},
        )

        res = client.get("/api/v1/pretrained/jobs?page=1&page_size=10")
        assert res.status_code == 200
        body = res.json()
        assert "items" in body
        assert "total" in body
        assert "page" in body
        assert "page_size" in body
        assert body["page"] == 1
        assert body["page_size"] == 10
        assert len(body["items"]) >= 1


class TestPretrainedJobDetailEndpoint:
    """GET /api/v1/pretrained/jobs/{job_id}"""

    def test_get_job_found(self, client: TestClient) -> None:
        create_res = client.post(
            "/api/v1/pretrained/infer",
            json={"source": "demo://detail.jpg", "model_version": "mock-v1"},
        )
        job_id = create_res.json()["id"]

        res = client.get(f"/api/v1/pretrained/jobs/{job_id}")
        assert res.status_code == 200
        body = res.json()
        assert body["id"] == job_id
        assert body["source"] == "demo://detail.jpg"

    def test_get_job_not_found(self, client: TestClient) -> None:
        res = client.get("/api/v1/pretrained/jobs/nonexistent-id")
        assert res.status_code == 404


class TestPretrainedJobsSummaryEndpoint:
    """GET /api/v1/pretrained/jobs/summary"""

    def test_summary_returns_counts(self, client: TestClient) -> None:
        res = client.get("/api/v1/pretrained/jobs/summary")
        assert res.status_code == 200
        body = res.json()
        assert "total" in body
        assert "queued" in body
        assert "running" in body
        assert "success" in body
        assert "failed" in body
        assert isinstance(body["total"], int)
