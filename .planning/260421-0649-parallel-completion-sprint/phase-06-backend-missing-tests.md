# Phase 06: Backend Missing Endpoint Tests

**Ưu tiên**: 🟢 Coverage
**Branch**: `test/missing-endpoints`
**Worktree**: Main (chỉ thêm file tests, không conflict)
**Ước tính**: 1-2 giờ

---

## Bối cảnh

Audit phát hiện backend có **22 endpoints** (không phải 18 như báo cáo). Các endpoint chưa có test:

1. `GET /api/v1/accounts` (list, khác với detail `/{plate}`)
2. `GET /api/v1/import-batches`
3. `GET /api/v1/import-batches/summary`
4. `GET /api/v1/errors/sample`

Backend tests hiện tại: 56/56 pass nhưng chỉ cover ~18 endpoints.

---

## Yêu cầu

### 1. Đọc code các endpoint

File `apps/backend/app/main.py`:
- Line 111: `/api/v1/accounts` list endpoint
- Line 180: `/api/v1/import-batches`
- Line 200: `/api/v1/import-batches/summary`
- Line 330: `/api/v1/errors/sample`

Hiểu response schema từ `apps/backend/app/schemas.py`.

### 2. Viết tests

File mới: `apps/backend/tests/test_accounts_list.py`
```python
def test_list_accounts_empty(client):
    r = client.get("/api/v1/accounts")
    assert r.status_code == 200
    assert r.json() == []  # or has pagination structure

def test_list_accounts_with_data(client, seed_accounts):
    r = client.get("/api/v1/accounts?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) <= 5

def test_list_accounts_filter_by_plate(client, seed_accounts):
    r = client.get("/api/v1/accounts?plate=29A")
    # verify returns only plates starting with 29A

def test_list_accounts_sort_by_balance(client, seed_accounts):
    r = client.get("/api/v1/accounts?sort=balance_desc")
    # verify sorted desc
```

File mới: `apps/backend/tests/test_import_batches.py`
```python
def test_list_import_batches_empty(client):
    r = client.get("/api/v1/import-batches")
    assert r.status_code == 200

def test_import_batches_summary(client):
    r = client.get("/api/v1/import-batches/summary")
    assert r.status_code == 200
    # verify fields: total_batches, imported, skipped, invalid
```

File mới: `apps/backend/tests/test_errors_sample.py`
```python
def test_errors_sample_endpoint(client):
    r = client.get("/api/v1/errors/sample")
    assert r.status_code == 200
    # verify response schema
```

### 3. Fixtures

Tạo fixture `seed_accounts` trong `conftest.py` hoặc các file test:
- 5-10 accounts với balance + status khác nhau
- Test pagination, filter, sort

### 4. Run full suite

```bash
cd apps/backend && PYTHONIOENCODING=utf-8 python -m pytest tests/ -v
```

Target: 56 + N new tests (ước tính +10-15 tests) = **66-71 tests pass**.

---

## Files ownership

- `apps/backend/tests/test_accounts_list.py` (MỚI)
- `apps/backend/tests/test_import_batches.py` (MỚI)
- `apps/backend/tests/test_errors_sample.py` (MỚI)
- `apps/backend/tests/conftest.py` (CÓ THỂ sửa: thêm fixture nếu chưa có)

---

## Tiêu chí thành công

- [ ] Tổng tests ≥ 66 (56 cũ + 10 mới tối thiểu)
- [ ] Tất cả pass
- [ ] Coverage ≥ 85% (đo bằng `pytest --cov=app`)
- [ ] Các edge case cover: empty, with data, filter, sort, invalid params

---

## Rủi ro

- Thấp — chỉ thêm test, không sửa logic
- Có thể phát hiện bug trong endpoint hiện có → ghi log, không fix trong phase này (tạo issue riêng)

---

## Output

- Branch `test/missing-endpoints` với tests mới
- Report ngắn: `test_plans_and_reports/test12-backend-coverage.md` (list endpoints đã cover + các bug phát hiện)
- Merge ngay nếu pass (không phụ thuộc phase khác)
