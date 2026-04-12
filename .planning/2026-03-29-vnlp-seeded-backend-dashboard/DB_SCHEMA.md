# DB Schema (Seeded Mode Draft v1)
## He thong seeded plates + backend nghiep vu + dashboard

**Pham vi**: 1 stream logic, seeded plate import, rule so du `100000 VND` va `-2000 VND` moi luot.

---

## 1) Bang `cameras`
```sql
CREATE TABLE cameras (
  id              UUID PRIMARY KEY,
  name            TEXT NOT NULL,
  gate_type       TEXT NOT NULL CHECK (gate_type IN ('student','staff')),
  location        TEXT,
  stream_url      TEXT,
  is_active       BOOLEAN NOT NULL DEFAULT TRUE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## 2) Bang `vehicle_events`
```sql
CREATE TABLE vehicle_events (
  id              UUID PRIMARY KEY,
  camera_id       UUID NOT NULL REFERENCES cameras(id),
  timestamp       TIMESTAMPTZ NOT NULL,
  direction       TEXT NOT NULL CHECK (direction IN ('in','out')),
  vehicle_type    TEXT NOT NULL CHECK (vehicle_type IN ('motorbike','car')),
  track_id        TEXT NOT NULL,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## 3) Bang `plate_reads`
```sql
CREATE TABLE plate_reads (
  id              UUID PRIMARY KEY,
  event_id        UUID NOT NULL REFERENCES vehicle_events(id) ON DELETE CASCADE,
  plate_text      TEXT,
  confidence      NUMERIC,
  snapshot_url    TEXT,
  crop_url        TEXT,
  ocr_status      TEXT NOT NULL CHECK (ocr_status IN ('success','partial','failed')),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## 4) Bang `accounts`
```sql
CREATE TABLE accounts (
  id                   UUID PRIMARY KEY,
  plate_text           TEXT NOT NULL UNIQUE,
  balance_vnd          INTEGER NOT NULL,
  registration_status  TEXT NOT NULL CHECK (
    registration_status IN ('registered','temporary_registered','unknown')
  ),
  created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## 5) Bang `transactions`
```sql
CREATE TABLE transactions (
  id                  UUID PRIMARY KEY,
  account_id          UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
  event_id            UUID REFERENCES vehicle_events(id),
  amount_vnd          INTEGER NOT NULL,
  balance_after_vnd   INTEGER NOT NULL,
  type                TEXT NOT NULL CHECK (type IN ('init','event_charge','manual_adjust')),
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## 6) Bang `barrier_actions`
```sql
CREATE TABLE barrier_actions (
  id                   UUID PRIMARY KEY,
  event_id             UUID NOT NULL REFERENCES vehicle_events(id) ON DELETE CASCADE,
  plate_text           TEXT,
  registration_status  TEXT NOT NULL CHECK (
    registration_status IN ('registered','temporary_registered','unknown')
  ),
  barrier_action       TEXT NOT NULL CHECK (barrier_action IN ('open','hold')),
  barrier_reason       TEXT NOT NULL,
  needs_verification   BOOLEAN NOT NULL DEFAULT FALSE,
  verified_by          TEXT,
  verified_at          TIMESTAMPTZ,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## 7) Bang `audit_logs`
```sql
CREATE TABLE audit_logs (
  id              UUID PRIMARY KEY,
  user_id         TEXT,
  action          TEXT NOT NULL,
  metadata_json   JSONB,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 8) Index khuyen nghi
```sql
CREATE INDEX idx_vehicle_events_timestamp ON vehicle_events(timestamp DESC);
CREATE INDEX idx_vehicle_events_camera_timestamp ON vehicle_events(camera_id, timestamp DESC);
CREATE INDEX idx_vehicle_events_track ON vehicle_events(track_id);

CREATE INDEX idx_plate_reads_plate ON plate_reads(plate_text);
CREATE INDEX idx_plate_reads_status ON plate_reads(ocr_status);

CREATE INDEX idx_accounts_plate ON accounts(plate_text);
CREATE INDEX idx_accounts_registration_status ON accounts(registration_status);

CREATE INDEX idx_transactions_account_time ON transactions(account_id, created_at DESC);
CREATE INDEX idx_barrier_actions_plate_time ON barrier_actions(plate_text, created_at DESC);
CREATE INDEX idx_audit_logs_time ON audit_logs(created_at DESC);
```

---

## 9) Rule nghiep vu tai chinh
- Khi import seed plate lan dau:
  - tao account voi `balance_vnd = 100000`
  - tao transaction `type='init'`, `amount_vnd=100000`
- Moi event in/out co `plate_text` hop le:
  - tru `2000 VND`
  - tao transaction `type='event_charge'`, `amount_vnd=-2000`
- Cho phep so du am.

---

## 10) Rule nghiep vu barrier
- `registered + in` => `open`
- `registered + out` => `open`
- `temporary_registered + in` => `open`
- `temporary_registered + out` => `hold`
- `unknown + in` => chuyen thanh `temporary_registered` va `open`
- verify thanh cong => `hold -> open`

---

## 11) Provenance metadata (phase sau)
Khong bat buoc cho MVP, nhung co the bo sung sau:

### Lua chon A - Them cot vao `accounts`
```sql
ALTER TABLE accounts
ADD COLUMN source TEXT,
ADD COLUMN seed_group TEXT,
ADD COLUMN imported_at TIMESTAMPTZ;
```

### Lua chon B - Tao bang `import_batches`
```sql
CREATE TABLE import_batches (
  id              UUID PRIMARY KEY,
  source          TEXT NOT NULL,
  seed_group      TEXT NOT NULL,
  imported_by     TEXT,
  imported_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  total_rows      INTEGER NOT NULL,
  imported_rows   INTEGER NOT NULL,
  skipped_rows    INTEGER NOT NULL,
  invalid_rows    INTEGER NOT NULL
);
```

Khuyen nghi:
- MVP khong them bang moi
- phase sau moi bo sung provenance chi tiet

---

## 12) Quan he du lieu chinh
- `cameras (1) -> (N) vehicle_events`
- `vehicle_events (1) -> (0..1) plate_reads`
- `accounts (1) -> (N) transactions`
- `vehicle_events (1) -> (0..N) transactions`
- `vehicle_events (1) -> (0..N) barrier_actions`

---

## 13) Merge note
File nay co chu dich giu ten va style gan voi `.artifacts/DB_SCHEMA.md`.

Khi merge ve `.artifacts`, uu tien:
- dung schema hien dang khop codebase thuc te
- giu phan provenance thanh optional extension
- ghi ro `seeded mode` la mot operational profile, khong phai schema song song khac

