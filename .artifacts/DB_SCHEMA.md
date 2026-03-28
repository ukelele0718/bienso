# DB Schema (Draft v1)
## Hệ thống đếm xe + nhận dạng biển số + ví theo biển số

**Phạm vi**: 1 camera stream, 2 loại cổng, rule số dư 100,000 VND và -2,000 VND mỗi lượt.

---

## 1) Bảng `cameras`
```sql
CREATE TABLE cameras (
  id              UUID PRIMARY KEY,
  name            VARCHAR(100) NOT NULL,
  gate_type       VARCHAR(20) NOT NULL CHECK (gate_type IN ('student_gate','lecturer_gate')),
  location        VARCHAR(255),
  stream_url      TEXT NOT NULL,
  is_active       BOOLEAN NOT NULL DEFAULT TRUE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## 2) Bảng `vehicle_events`
```sql
CREATE TABLE vehicle_events (
  id              UUID PRIMARY KEY,
  camera_id       UUID NOT NULL REFERENCES cameras(id),
  event_time      TIMESTAMPTZ NOT NULL,
  direction       VARCHAR(10) NOT NULL CHECK (direction IN ('in','out')),
  vehicle_type    VARCHAR(20) NOT NULL CHECK (vehicle_type IN ('motorbike','car')),
  track_id        VARCHAR(64) NOT NULL,
  snapshot_url    TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## 3) Bảng `plate_reads`
```sql
CREATE TABLE plate_reads (
  id              UUID PRIMARY KEY,
  event_id        UUID NOT NULL UNIQUE REFERENCES vehicle_events(id) ON DELETE CASCADE,
  plate_text      VARCHAR(20),
  confidence      NUMERIC(5,4),
  ocr_status      VARCHAR(20) NOT NULL CHECK (ocr_status IN ('success','failed','partial')),
  crop_url        TEXT,
  raw_text        VARCHAR(32),
  normalized_text VARCHAR(20),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## 4) Bảng `accounts`
```sql
CREATE TABLE accounts (
  id              UUID PRIMARY KEY,
  plate_text      VARCHAR(20) NOT NULL UNIQUE,
  balance_vnd     BIGINT NOT NULL,
  registration_status VARCHAR(30) NOT NULL CHECK (registration_status IN ('registered','temporary_registered','unknown')),
  is_active       BOOLEAN NOT NULL DEFAULT TRUE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## 5) Bảng `transactions`
```sql
CREATE TABLE transactions (
  id                  UUID PRIMARY KEY,
  account_id          UUID NOT NULL REFERENCES accounts(id),
  event_id            UUID REFERENCES vehicle_events(id),
  tx_type             VARCHAR(20) NOT NULL CHECK (tx_type IN ('init','event_charge','manual_adjust')),
  amount_vnd          BIGINT NOT NULL,
  balance_before_vnd  BIGINT NOT NULL,
  balance_after_vnd   BIGINT NOT NULL,
  note                TEXT,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## 6) Bảng `users`
```sql
CREATE TABLE users (
  id              UUID PRIMARY KEY,
  username        VARCHAR(64) NOT NULL UNIQUE,
  full_name       VARCHAR(120),
  role            VARCHAR(20) NOT NULL CHECK (role IN ('guard','admin','student_view')),
  password_hash   TEXT NOT NULL,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## 7) Bảng `barrier_actions`
```sql
CREATE TABLE barrier_actions (
  id              UUID PRIMARY KEY,
  event_id        UUID NOT NULL REFERENCES vehicle_events(id) ON DELETE CASCADE,
  action          VARCHAR(10) NOT NULL CHECK (action IN ('open','hold')),
  reason          VARCHAR(100) NOT NULL,
  needs_verification BOOLEAN NOT NULL DEFAULT FALSE,
  verified_by     UUID REFERENCES users(id),
  verified_at     TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## 8) Bảng `audit_logs`
```sql
CREATE TABLE audit_logs (
  id              UUID PRIMARY KEY,
  user_id         UUID REFERENCES users(id),
  action          VARCHAR(100) NOT NULL,
  target_type     VARCHAR(50),
  target_id       VARCHAR(100),
  metadata_json   JSONB,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 8) Index khuyến nghị
```sql
CREATE INDEX idx_vehicle_events_time ON vehicle_events(event_time DESC);
CREATE INDEX idx_vehicle_events_camera_time ON vehicle_events(camera_id, event_time DESC);
CREATE INDEX idx_vehicle_events_track ON vehicle_events(track_id);

CREATE INDEX idx_plate_reads_plate ON plate_reads(plate_text);
CREATE INDEX idx_plate_reads_status ON plate_reads(ocr_status);

CREATE INDEX idx_transactions_account_time ON transactions(account_id, created_at DESC);
CREATE INDEX idx_transactions_event ON transactions(event_id);

CREATE INDEX idx_audit_logs_time ON audit_logs(created_at DESC);
```

---

## 9) Rule nghiệp vụ tài chính
- Khi biển số xuất hiện lần đầu (và OCR success):
  - tạo account với `balance_vnd = 100000`
  - tạo transaction `tx_type='init'`, `amount_vnd=100000`
- Mỗi event in/out có biển số hợp lệ:
  - trừ `2000` VND
  - tạo transaction `tx_type='event_charge'`, `amount_vnd=-2000`
- Cho phép số dư âm (không chặn trừ tiền).

---

## 10) Quan hệ dữ liệu chính
- `cameras (1) -> (N) vehicle_events`
- `vehicle_events (1) -> (0..1) plate_reads`
- `accounts (1) -> (N) transactions`
- `vehicle_events (1) -> (0..N) transactions` (thường 1 event = 1 transaction charge)
