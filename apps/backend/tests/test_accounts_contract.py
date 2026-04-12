from __future__ import annotations


def _create_event(client, plate_text: str) -> None:
    payload = {
        'camera_id': '11111111-1111-1111-1111-111111111111',
        'timestamp': '2026-04-10T10:00:00Z',
        'direction': 'in',
        'vehicle_type': 'motorbike',
        'track_id': f'track-{plate_text}',
        'plate_text': plate_text,
        'confidence': 0.95,
        'snapshot_url': 'http://example.com/snapshot.jpg',
    }
    res = client.post('/api/v1/events', json=payload)
    assert res.status_code == 200


def test_accounts_list_contract_has_sort_fields(client) -> None:
    _create_event(client, '99X99999')
    _create_event(client, '51G12345')

    res = client.get('/api/v1/accounts?sort_by=plate_text&sort_order=asc&page=1&page_size=20')
    assert res.status_code == 200

    payload = res.json()
    assert payload['sort_by'] == 'plate_text'
    assert payload['sort_order'] == 'asc'
    assert isinstance(payload['items'], list)

    plate_values = [row['plate_text'] for row in payload['items']]
    assert plate_values == sorted(plate_values)
