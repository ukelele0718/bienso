from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import ImportBatch

TEST_CAMERA_ID = "11111111-1111-1111-1111-111111111111"


def _create_event(client, plate_text: str) -> None:
    """Helper to create an event."""
    payload = {
        "camera_id": TEST_CAMERA_ID,
        "timestamp": datetime.now(UTC).isoformat(),
        "direction": "in",
        "vehicle_type": "motorbike",
        "track_id": f"track-{plate_text}",
        "plate_text": plate_text,
        "confidence": 0.95,
        "snapshot_url": None,
    }
    res = client.post("/api/v1/events", json=payload)
    assert res.status_code == 200


def test_get_import_batches_empty_state(client: TestClient) -> None:
    """Test list import batches returns empty when no batches exist."""
    res = client.get("/api/v1/import-batches")
    assert res.status_code == 200

    payload = res.json()
    assert isinstance(payload, list)
    assert len(payload) == 0


def test_get_import_batches_with_seeded_data(client: TestClient, db_session: Session) -> None:
    """Test list import batches returns seeded batches."""
    batch1 = ImportBatch(
        id=str(uuid4()),
        source="test_source_1",
        seed_group="group_a",
        imported_count=10,
        skipped_count=2,
        invalid_count=1,
    )
    batch2 = ImportBatch(
        id=str(uuid4()),
        source="test_source_2",
        seed_group="group_b",
        imported_count=20,
        skipped_count=3,
        invalid_count=2,
    )
    db_session.add(batch1)
    db_session.add(batch2)
    db_session.commit()

    res = client.get("/api/v1/import-batches")
    assert res.status_code == 200

    payload = res.json()
    assert len(payload) >= 2
    assert isinstance(payload, list)

    sources = [batch["source"] for batch in payload]
    assert "test_source_1" in sources
    assert "test_source_2" in sources


def test_get_import_batches_respects_limit(client: TestClient, db_session: Session) -> None:
    """Test list import batches respects limit parameter."""
    for i in range(5):
        batch = ImportBatch(
            id=str(uuid4()),
            source=f"source_{i}",
            imported_count=10 + i,
            skipped_count=1,
            invalid_count=0,
        )
        db_session.add(batch)
    db_session.commit()

    res = client.get("/api/v1/import-batches?limit=3")
    assert res.status_code == 200

    payload = res.json()
    assert len(payload) <= 3


def test_get_import_batches_default_limit_20(client: TestClient, db_session: Session) -> None:
    """Test default limit is 20."""
    for i in range(25):
        batch = ImportBatch(
            id=str(uuid4()),
            source=f"source_default_{i}",
            imported_count=5,
            skipped_count=0,
            invalid_count=0,
        )
        db_session.add(batch)
    db_session.commit()

    res = client.get("/api/v1/import-batches")
    assert res.status_code == 200

    payload = res.json()
    assert len(payload) <= 20


def test_get_import_batches_response_structure(client: TestClient, db_session: Session) -> None:
    """Test batch response includes all required fields."""
    batch = ImportBatch(
        id=str(uuid4()),
        source="test_structure",
        seed_group="group_test",
        imported_count=15,
        skipped_count=2,
        invalid_count=1,
    )
    db_session.add(batch)
    db_session.commit()

    res = client.get("/api/v1/import-batches?limit=1")
    assert res.status_code == 200

    payload = res.json()
    assert len(payload) >= 1

    batch_item = payload[0]
    assert "id" in batch_item
    assert "source" in batch_item
    assert "seed_group" in batch_item
    assert "imported_count" in batch_item
    assert "skipped_count" in batch_item
    assert "invalid_count" in batch_item
    assert "created_at" in batch_item


def test_get_import_batches_ordered_by_created_at_desc(client: TestClient, db_session: Session) -> None:
    """Test batches are ordered by created_at descending (most recent first)."""
    batch1 = ImportBatch(
        id=str(uuid4()),
        source="batch_old",
        imported_count=1,
        skipped_count=0,
        invalid_count=0,
    )
    db_session.add(batch1)
    db_session.commit()

    batch2 = ImportBatch(
        id=str(uuid4()),
        source="batch_new",
        imported_count=2,
        skipped_count=0,
        invalid_count=0,
    )
    db_session.add(batch2)
    db_session.commit()

    res = client.get("/api/v1/import-batches?limit=100")
    assert res.status_code == 200

    payload = res.json()
    # Most recent batch should appear first
    if len(payload) >= 2:
        assert payload[0]["created_at"] >= payload[1]["created_at"]


def test_get_import_batches_summary_responds_with_counts(client: TestClient) -> None:
    """Test summary returns all required count fields."""
    res = client.get("/api/v1/import-batches/summary")
    assert res.status_code == 200

    payload = res.json()
    assert "total_batches" in payload
    assert "total_imported" in payload
    assert "total_skipped" in payload
    assert "total_invalid" in payload
    assert isinstance(payload["total_batches"], int)
    assert isinstance(payload["total_imported"], int)
    assert isinstance(payload["total_skipped"], int)
    assert isinstance(payload["total_invalid"], int)
    assert payload["total_batches"] >= 0
    assert payload["total_imported"] >= 0
    assert payload["total_skipped"] >= 0
    assert payload["total_invalid"] >= 0


def test_get_import_batches_summary_aggregates_counts(client: TestClient, db_session: Session) -> None:
    """Test summary correctly aggregates counts across batches."""
    batch1 = ImportBatch(
        id=str(uuid4()),
        source="summary_test_1",
        imported_count=10,
        skipped_count=2,
        invalid_count=1,
    )
    batch2 = ImportBatch(
        id=str(uuid4()),
        source="summary_test_2",
        imported_count=20,
        skipped_count=3,
        invalid_count=2,
    )
    db_session.add(batch1)
    db_session.add(batch2)
    db_session.commit()

    res = client.get("/api/v1/import-batches/summary")
    assert res.status_code == 200

    payload = res.json()
    assert payload["total_batches"] >= 2
    assert payload["total_imported"] >= 30
    assert payload["total_skipped"] >= 5
    assert payload["total_invalid"] >= 3


def test_get_import_batches_summary_response_structure(client: TestClient, db_session: Session) -> None:
    """Test summary response includes all required fields."""
    batch = ImportBatch(
        id=str(uuid4()),
        source="summary_structure",
        imported_count=5,
        skipped_count=1,
        invalid_count=0,
    )
    db_session.add(batch)
    db_session.commit()

    res = client.get("/api/v1/import-batches/summary")
    assert res.status_code == 200

    payload = res.json()
    assert "total_batches" in payload
    assert "total_imported" in payload
    assert "total_skipped" in payload
    assert "total_invalid" in payload


def test_get_import_batches_with_null_seed_group(client: TestClient, db_session: Session) -> None:
    """Test batch with null seed_group is handled correctly."""
    batch = ImportBatch(
        id=str(uuid4()),
        source="null_seed_source",
        seed_group=None,
        imported_count=5,
        skipped_count=0,
        invalid_count=0,
    )
    db_session.add(batch)
    db_session.commit()

    res = client.get("/api/v1/import-batches?limit=1")
    assert res.status_code == 200

    payload = res.json()
    assert len(payload) >= 1
    # seed_group should be present (possibly null)
    assert "seed_group" in payload[0]


def test_get_import_batches_limit_invalid_zero(client: TestClient) -> None:
    """Test invalid limit (0) returns validation error."""
    res = client.get("/api/v1/import-batches?limit=0")
    assert res.status_code == 422


def test_get_import_batches_limit_invalid_negative(client: TestClient) -> None:
    """Test invalid limit (negative) returns validation error."""
    res = client.get("/api/v1/import-batches?limit=-1")
    assert res.status_code == 422


def test_get_import_batches_limit_invalid_exceeds_max(client: TestClient) -> None:
    """Test invalid limit (>100) returns validation error."""
    res = client.get("/api/v1/import-batches?limit=101")
    assert res.status_code == 422
