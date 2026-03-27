from __future__ import annotations

from datetime import datetime

from fastapi.testclient import TestClient


def test_balance_rule_init_and_charge(client: TestClient) -> None:
    plate = "29A-99999"

    payload = {
        "camera_id": "11111111-1111-1111-1111-111111111111",
        "timestamp": datetime.utcnow().isoformat(),
        "direction": "in",
        "vehicle_type": "motorbike",
        "track_id": "track-001",
        "plate_text": plate,
        "confidence": 0.95,
        "snapshot_url": None,
    }

    create_res = client.post("/api/v1/events", json=payload)
    assert create_res.status_code == 200

    account_res = client.get(f"/api/v1/accounts/{plate}")
    assert account_res.status_code == 200
    assert account_res.json()["balance_vnd"] == 98_000

    tx_res = client.get(f"/api/v1/accounts/{plate}/transactions")
    assert tx_res.status_code == 200
    txs = tx_res.json()
    assert len(txs) == 2
    assert txs[0]["type"] == "init"
    assert txs[1]["type"] == "event_charge"


def test_balance_can_be_negative(client: TestClient) -> None:
    plate = "30F-00001"

    for i in range(60):
        payload = {
            "camera_id": "11111111-1111-1111-1111-111111111111",
            "timestamp": datetime.utcnow().isoformat(),
            "direction": "in" if i % 2 == 0 else "out",
            "vehicle_type": "motorbike",
            "track_id": f"track-{i}",
            "plate_text": plate,
            "confidence": 0.95,
            "snapshot_url": None,
        }
        res = client.post("/api/v1/events", json=payload)
        assert res.status_code == 200

    account_res = client.get(f"/api/v1/accounts/{plate}")
    assert account_res.status_code == 200
    assert account_res.json()["balance_vnd"] < 0
