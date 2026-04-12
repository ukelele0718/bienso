from __future__ import annotations


def test_account_not_found_uses_standard_error_contract(client) -> None:
    res = client.get('/api/v1/accounts/NOTFOUND123')
    assert res.status_code == 404
    payload = res.json()
    assert payload['code'] == 'account_not_found'
    assert isinstance(payload['message'], str)
    assert 'details' in payload
