from __future__ import annotations

from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Account

TEST_CAMERA_ID = "11111111-1111-1111-1111-111111111111"


def _create_event(client, plate_text: str, direction: str = "in") -> None:
    """Helper to create an event which auto-generates account."""
    payload = {
        "camera_id": TEST_CAMERA_ID,
        "timestamp": datetime.now(UTC).isoformat(),
        "direction": direction,
        "vehicle_type": "motorbike",
        "track_id": f"track-{plate_text}",
        "plate_text": plate_text,
        "confidence": 0.95,
        "snapshot_url": None,
    }
    res = client.post("/api/v1/events", json=payload)
    assert res.status_code == 200


def test_list_accounts_empty_state(client: TestClient) -> None:
    """Test list_accounts returns empty list when no accounts exist."""
    res = client.get("/api/v1/accounts")
    assert res.status_code == 200

    payload = res.json()
    assert payload["items"] == []
    assert payload["total"] == 0
    assert payload["page"] == 1
    assert payload["page_size"] == 20


def test_list_accounts_with_seeded_data(client: TestClient) -> None:
    """Test list_accounts returns seeded accounts."""
    _create_event(client, "51G12345")
    _create_event(client, "99X99999")

    res = client.get("/api/v1/accounts")
    assert res.status_code == 200

    payload = res.json()
    assert payload["total"] >= 2
    assert len(payload["items"]) >= 2
    plates = [item["plate_text"] for item in payload["items"]]
    assert "51G12345" in plates
    assert "99X99999" in plates


def test_list_accounts_pagination_page_1(client: TestClient) -> None:
    """Test pagination returns first page correctly."""
    for i in range(5):
        _create_event(client, f"51G{i:05d}")

    res = client.get("/api/v1/accounts?page=1&page_size=3")
    assert res.status_code == 200

    payload = res.json()
    assert payload["page"] == 1
    assert payload["page_size"] == 3
    assert len(payload["items"]) == 3
    assert payload["total"] >= 5


def test_list_accounts_pagination_page_2(client: TestClient) -> None:
    """Test pagination returns second page correctly."""
    for i in range(5):
        _create_event(client, f"99X{i:05d}")

    res = client.get("/api/v1/accounts?page=2&page_size=3")
    assert res.status_code == 200

    payload = res.json()
    assert payload["page"] == 2
    assert payload["page_size"] == 3


def test_list_accounts_filter_by_plate(client: TestClient) -> None:
    """Test filter accounts by plate substring."""
    _create_event(client, "51G12345")
    _create_event(client, "99X54321")

    res = client.get("/api/v1/accounts?plate=51G")
    assert res.status_code == 200

    payload = res.json()
    plates = [item["plate_text"] for item in payload["items"]]
    for plate in plates:
        assert "51G" in plate


def test_list_accounts_filter_by_registration_status(client: TestClient, db_session: Session) -> None:
    """Test filter accounts by registration status."""
    _create_event(client, "51G11111")

    # Mark one as registered manually
    acc = db_session.query(Account).filter_by(plate_text="51G11111").first()
    assert acc is not None
    acc.registration_status = "registered"
    db_session.commit()

    res = client.get("/api/v1/accounts?registration_status=registered")
    assert res.status_code == 200

    payload = res.json()
    assert len(payload["items"]) >= 1
    for item in payload["items"]:
        assert item["registration_status"] == "registered"


def test_list_accounts_sort_by_created_at_desc(client: TestClient) -> None:
    """Test sort by created_at descending (most recent first)."""
    _create_event(client, "51G00001")
    _create_event(client, "51G00002")
    _create_event(client, "51G00003")

    res = client.get("/api/v1/accounts?sort_by=created_at&sort_order=desc&page_size=100")
    assert res.status_code == 200

    payload = res.json()
    assert payload["sort_by"] == "created_at"
    assert payload["sort_order"] == "desc"
    # Most recent items should appear first due to DESC order


def test_list_accounts_sort_by_plate_text_asc(client: TestClient) -> None:
    """Test sort by plate_text ascending (alphabetical)."""
    _create_event(client, "99X99999")
    _create_event(client, "51G12345")
    _create_event(client, "30F88888")

    res = client.get("/api/v1/accounts?sort_by=plate_text&sort_order=asc&page_size=100")
    assert res.status_code == 200

    payload = res.json()
    assert payload["sort_by"] == "plate_text"
    assert payload["sort_order"] == "asc"

    plates = [item["plate_text"] for item in payload["items"]]
    assert plates == sorted(plates)


def test_list_accounts_sort_by_balance_vnd(client: TestClient, db_session: Session) -> None:
    """Test sort by balance_vnd."""
    _create_event(client, "51G22222")
    _create_event(client, "99X33333")

    # Manually adjust balances
    acc1 = db_session.query(Account).filter_by(plate_text="51G22222").first()
    acc2 = db_session.query(Account).filter_by(plate_text="99X33333").first()
    if acc1 and acc2:
        acc1.balance_vnd = 50000
        acc2.balance_vnd = 100000
        db_session.commit()

    res = client.get("/api/v1/accounts?sort_by=balance_vnd&sort_order=asc&page_size=100")
    assert res.status_code == 200

    payload = res.json()
    assert payload["sort_by"] == "balance_vnd"
    assert payload["sort_order"] == "asc"

    balances = [item["balance_vnd"] for item in payload["items"]]
    assert balances == sorted(balances)


def test_list_accounts_invalid_page_returns_error(client: TestClient) -> None:
    """Test invalid page number (0 or negative) returns validation error."""
    res = client.get("/api/v1/accounts?page=0")
    assert res.status_code == 422  # Unprocessable entity


def test_list_accounts_invalid_page_size_returns_error(client: TestClient) -> None:
    """Test invalid page_size (0 or >100) returns validation error."""
    res = client.get("/api/v1/accounts?page_size=0")
    assert res.status_code == 422

    res = client.get("/api/v1/accounts?page_size=101")
    assert res.status_code == 422


def test_list_accounts_response_has_required_fields(client: TestClient) -> None:
    """Test response includes all required fields."""
    _create_event(client, "51G77777")

    res = client.get("/api/v1/accounts")
    assert res.status_code == 200

    payload = res.json()
    assert "items" in payload
    assert "total" in payload
    assert "page" in payload
    assert "page_size" in payload
    assert "sort_by" in payload
    assert "sort_order" in payload

    # Verify item structure
    if payload["items"]:
        item = payload["items"][0]
        assert "plate_text" in item
        assert "balance_vnd" in item
        assert "registration_status" in item


def test_list_accounts_large_page_size(client: TestClient) -> None:
    """Test respects max page_size limit of 100."""
    for i in range(5):
        _create_event(client, f"51G1000{i}")

    # Request with size > 100 should be capped at 100
    res = client.get("/api/v1/accounts?page_size=100")
    assert res.status_code == 200

    payload = res.json()
    assert payload["page_size"] == 100
