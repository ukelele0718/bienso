from __future__ import annotations


def _create_event(client, plate_text: str, direction: str = "in") -> None:
    payload = {
        "camera_id": "11111111-1111-1111-1111-111111111111",
        "timestamp": "2026-04-10T10:00:00Z",
        "direction": direction,
        "vehicle_type": "motorbike",
        "track_id": f"track-{plate_text}-{direction}",
        "plate_text": plate_text,
        "confidence": 0.95,
        "snapshot_url": "http://example.com/snapshot.jpg",
    }
    res = client.post("/api/v1/events", json=payload)
    assert res.status_code == 200


def test_seeded_and_pretrained_smoke_api(client) -> None:
    _create_event(client, "51G12345", "in")
    _create_event(client, "99X99999", "out")

    realtime = client.get("/api/v1/stats/realtime")
    assert realtime.status_code == 200

    traffic = client.get("/api/v1/stats/traffic?group_by=hour")
    assert traffic.status_code == 200

    accounts = client.get("/api/v1/accounts?sort_by=plate_text&sort_order=asc&page=1&page_size=10")
    assert accounts.status_code == 200
    accounts_payload = accounts.json()
    assert accounts_payload["sort_by"] == "plate_text"
    assert accounts_payload["sort_order"] == "asc"

    barrier_actions = client.get("/api/v1/barrier-actions")
    assert barrier_actions.status_code == 200

    import_summary = client.get("/api/v1/import-batches/summary")
    assert import_summary.status_code == 200

    infer_job = client.post(
        "/api/v1/pretrained/infer",
        json={"model_version": "mock-v1", "source": "demo://frame-001.jpg", "threshold": 0.5},
    )
    assert infer_job.status_code == 200

    import_job = client.post(
        "/api/v1/pretrained/import",
        json={
            "model_version": "mock-v1",
            "source": "demo://batch-001",
            "items": [
                {"plate_text": "51G12345", "confidence": 0.9, "vehicle_type": "motorbike"},
                {"plate_text": "99X99999", "confidence": 0.8, "vehicle_type": "car"},
            ],
        },
    )
    assert import_job.status_code == 200

    jobs = client.get("/api/v1/pretrained/jobs?page=1&page_size=10")
    assert jobs.status_code == 200
    jobs_payload = jobs.json()
    assert jobs_payload["total"] >= 2

    summary = client.get("/api/v1/pretrained/jobs/summary")
    assert summary.status_code == 200

    job_id = import_job.json()["id"]
    detail = client.get(f"/api/v1/pretrained/jobs/{job_id}")
    assert detail.status_code == 200
    detail_payload = detail.json()
    assert detail_payload["id"] == job_id
    assert isinstance(detail_payload.get("items") or [], list)
