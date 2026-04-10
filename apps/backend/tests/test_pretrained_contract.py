from __future__ import annotations


def test_pretrained_jobs_summary_contract(client) -> None:
    res = client.get('/api/v1/pretrained/jobs/summary')
    assert res.status_code == 200

    payload = res.json()
    assert set(payload.keys()) == {"total", "queued", "running", "success", "failed"}
    assert payload["total"] >= 0
