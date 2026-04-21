from __future__ import annotations

from fastapi.testclient import TestClient


def test_get_error_sample_returns_success(client: TestClient) -> None:
    """Test /api/v1/errors/sample returns 200 status."""
    res = client.get("/api/v1/errors/sample")
    assert res.status_code == 200


def test_get_error_sample_response_structure(client: TestClient) -> None:
    """Test response includes required 'detail' field."""
    res = client.get("/api/v1/errors/sample")
    assert res.status_code == 200

    payload = res.json()
    assert "detail" in payload
    assert isinstance(payload["detail"], str)


def test_get_error_sample_returns_not_implemented(client: TestClient) -> None:
    """Test response returns 'not_implemented' detail message."""
    res = client.get("/api/v1/errors/sample")
    assert res.status_code == 200

    payload = res.json()
    assert payload["detail"] == "not_implemented"


def test_get_error_sample_consistent_response(client: TestClient) -> None:
    """Test multiple calls return consistent response."""
    res1 = client.get("/api/v1/errors/sample")
    res2 = client.get("/api/v1/errors/sample")

    assert res1.status_code == res2.status_code
    assert res1.json() == res2.json()
