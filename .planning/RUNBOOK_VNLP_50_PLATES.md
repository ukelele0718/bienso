# RUNBOOK - Test Dashboard + Backend with 50 VNLP plates

**Branch**: `feat/vnlp-seeded-backend-dashboard`  
**Data source**: `G:\TTMT\datn\data\external\vnlp\VNLP_detection\detection\list_two_rows_label_xe_may.txt`  
**Goal**: Import 50 plates, seed events, verify backend APIs + dashboard UX.

---

## 0) Preconditions

- Postgres running on `localhost:5432` (db: `vehicle_lpr`)  
- Backend + Dashboard ready to run locally  
- File path above exists and readable  

---

## 1) Start backend & dashboard

```powershell
cd G:\TTMT\datn

docker compose up -d postgres backend

cd G:\TTMT\datn\apps\dashboard
npm run dev
```

Backend default: `http://localhost:8000`  
Dashboard default: `http://localhost:5173`

---

## 2) Extract 50 plates from VNLP file

Create a working CSV from the first 50 lines of the source file. This CSV is compatible with `scripts/import_seed_plates.py`.

```powershell
cd G:\TTMT\datn

python - <<'PY'
from pathlib import Path
import csv

src = Path(r"G:\TTMT\datn\data\external\vnlp\VNLP_detection\detection\list_two_rows_label_xe_may.txt")
out = Path(r"G:\TTMT\datn\data\processed\vnlp_50_seed.csv")

lines = src.read_text(encoding="utf-8").strip().splitlines()[:50]
rows = []
for line in lines:
    name = Path(line).name
    # file pattern: <idx>_<frame>_<cls>_<plate>_<x1>_<y1>_<x2>_<y2>.jpg
    plate = name.split("_")[3].upper()
    rows.append({
        "plate_text": plate,
        "source": "vnlp_50",
        "seed_group": "two_rows_label_xe_may",
        "vehicle_type": "motorbike",
        "note": name,
    })

out.parent.mkdir(parents=True, exist_ok=True)
with open(out, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["plate_text", "source", "seed_group", "vehicle_type", "note"],
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows -> {out}")
PY
```

Expected output: `data/processed/vnlp_50_seed.csv`

---

## 3) Import 50 plates into accounts

```powershell
cd G:\TTMT\datn
python scripts\import_seed_plates.py --csv G:\TTMT\datn\data\processed\vnlp_50_seed.csv
```

Expected:
- 50 plates imported (or promoted) in accounts
- `import_batches` row created

---

## 4) Seed 50 events for those plates (API)

This will create events + plate_reads so the dashboard has traffic and barrier activity.

```powershell
cd G:\TTMT\datn

python - <<'PY'
from pathlib import Path
import httpx
from datetime import datetime, UTC

src = Path(r"G:\TTMT\datn\data\external\vnlp\VNLP_detection\detection\list_two_rows_label_xe_may.txt")
base_url = "http://localhost:8000"

lines = src.read_text(encoding="utf-8").strip().splitlines()[:50]

payloads = []
for idx, line in enumerate(lines):
    name = Path(line).name
    parts = name.split("_")
    plate = parts[3].upper()
    payloads.append({
        "camera_id": "11111111-1111-1111-1111-111111111111",
        "timestamp": datetime.now(UTC).isoformat(),
        "direction": "in" if idx % 2 == 0 else "out",
        "vehicle_type": "motorbike",
        "track_id": name.rsplit(".", 1)[0],
        "plate_text": plate,
        "confidence": 0.9,
        "snapshot_url": f"file://{line}",
    })

with httpx.Client(base_url=base_url, timeout=30.0) as client:
    ok = 0
    for p in payloads:
        r = client.post("/api/v1/events", json=p)
        if r.status_code == 200:
            ok += 1
    print(f"Seeded events: {ok}/{len(payloads)}")
PY
```

---

## 5) Backend API checks (quick)

```powershell
curl "http://localhost:8000/api/v1/accounts?page=1&page_size=10&registration_status=registered&sort_by=plate_text&sort_order=asc"

curl "http://localhost:8000/api/v1/import-batches/summary"

curl "http://localhost:8000/api/v1/stats/realtime"

curl "http://localhost:8000/api/v1/stats/traffic?group_by=hour"
```

---

## 6) Dashboard manual checks

Open `http://localhost:5173` and verify:

### Seeded section
- KPI cards render (Total In/Out, OCR success)
- Traffic summary string renders
- Account list: filter by plate, sort by balance/plate, pagination
- Import summary shows total/imported/skipped/invalid
- Verify queue renders (empty state OK)

### Pretrained section (optional on this branch)
- Not required for this branch unless pretrained UI is present.

---

## 7) Done criteria

- 50 plates imported into accounts.
- 50 events posted successfully.
- Dashboard shows non-empty KPI + traffic + account list.
- No API errors in console/network.

---

## 8) Cleanup (optional)

If you need reset before re-run:

```powershell
cd G:\TTMT\datn
python scripts\reset_seeded_test_state.py
```
