# Dashboard Wireframe (Seeded Mode v1)
## Scope: account-first + search + verify queue + stats

---

## 1) Man hinh tong quan (Realtime / Seeded Operations)

### Layout
- Header: ten he thong, branch mode (`Seeded mode`), trang thai backend, thoi gian hien tai.
- Row KPI cards:
  - Tong account
  - Registered accounts
  - Temporary registered accounts
  - Barrier holds can verify
- Main content chia 2 cot:
  - Cot trai (65%): bang event / account activity gan nhat
  - Cot phai (35%): verify queue + summary

### Bang su kien / account activity
Cot de xuat:
- Thoi gian
- Bien so
- Loai xe
- Huong (in/out)
- Registration status
- Barrier action
- So du sau giao dich
- Action (xem chi tiet / verify neu can)

Luu y:
- Trong seeded mode, cot `confidence` va `OCR status` co the an hoac day xuong secondary.

---

## 2) Man hinh tra cuu su kien

### Bo loc
- Bien so (text)
- Khoang thoi gian (from/to)
- Huong (in/out)
- Loai xe (motorbike/car)
- Registration status
- Barrier action

### Ket qua
- Table phan trang.
- Nhan vao dong de mo panel chi tiet:
  - snapshot_url
  - plate_text
  - event metadata
  - barrier metadata
  - giao dich lien quan neu co

---

## 3) Man hinh tai khoan bien so

### Tim kiem
- Input bien so + nut tra cuu

### Thong tin chinh
- Bien so
- Registration status
- So du hien tai
- So luot in/out da ghi nhan
- Lan cap nhat cuoi

### Lich su giao dich
Cot:
- Thoi gian
- Loai giao dich (`init`, `event_charge`, `manual_adjust`)
- So tien (+/-)
- So du sau
- Event lien quan

---

## 4) Man hinh verify queue

### Muc tieu
Cho bao ve xu ly cac xe `temporary_registered` dang ra cong va bi `hold`.

### Bang verify queue
Cot:
- Thoi gian
- Bien so
- Registration status
- Barrier action
- Barrier reason
- Snapshot
- Verify action

### Hanh dong
- `Open after verify`
- `View history`

---

## 5) Man hinh thong ke

### Bieu do
- Luu luong theo gio
- Luu luong theo ngay
- So luong registered / temporary theo thoi gian
- Hold events theo gio/ngay

### Bo loc
- Range thoi gian
- Kich ban cong

Luu y:
- `OCR success rate` van co the giu o dashboard de khong vo layout, nhung trong seeded mode metric nay khong phai KPI chinh.

---

## 6) UX states bat buoc
- Loading state cho moi API call
- Empty state khi chua co du lieu
- Error state kem nut retry
- Badge cho:
  - `registered`
  - `temporary_registered`
  - `hold`
  - `open`

---

## 7) Wireframe ASCII (man tong quan)

```text
+--------------------------------------------------------------------------------+
| Seeded Plate Operations        Backend: ONLINE        Time: 2026-03-29 10:30  |
+--------------------------------------------------------------------------------+
| [Total Accounts: 3227] [Registered: 3200] [Temporary: 27] [Hold Queue: 5]     |
+-------------------------------------------+------------------------------------+
| Recent Events / Accounts                   | Verify Queue / Summary             |
|-------------------------------------------|------------------------------------|
| time  | plate    | dir | reg | action |bal| - 30B99999 waiting verify         |
| 10:29 | 29A12345 | IN  | REG | OPEN   |86k| - 29C88888 waiting verify         |
| 10:29 | 30B99999 | OUT | TMP | HOLD   |96k| - backend health: OK              |
| ...                                       |                                    |
+-------------------------------------------+------------------------------------+
```

---

## 8) Mapping voi API
- KPI cards:
  - `GET /api/v1/accounts/summary`
  - `GET /api/v1/stats/realtime`
- Activity table:
  - `GET /api/v1/events`
- Search page:
  - `GET /api/v1/events`
- Account page:
  - `GET /api/v1/accounts/{plate_text}`
  - `GET /api/v1/accounts/{plate_text}/transactions`
- Verify queue:
  - `GET /api/v1/barrier-actions?plate=...`
  - `POST /api/v1/barrier-actions/verify`
- Stats page:
  - `GET /api/v1/stats/traffic`

---

## 9) Uu tien giao dien cho seeded mode
- Uu tien `account list + detail + verify queue`
- Uu tien su ro rang cua barrier state hon la do phong phu cua AI metrics
- Khong can lam giao dien "camera first" trong phase nay

---

## 10) Merge note
File nay co chu dich giu ten va ket cau gan voi `.artifacts/DASHBOARD_WIREFRAME.md`.

Khi merge ve `.artifacts`, uu tien:
- giu layout tong quan / search / account / stats
- bo sung them man `verify queue` thanh mot section chinh
- coi seeded mode la cach sap xep uu tien giao dien trong giai doan backend-first MVP

