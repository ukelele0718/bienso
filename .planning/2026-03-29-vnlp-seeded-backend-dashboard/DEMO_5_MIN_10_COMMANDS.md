# DEMO SIEU NGAN 5 PHUT - 10 LENH

Muc tieu: trong ~5 phut, dung 10 lenh de chay va chung minh seeded flow end-to-end.

Workspace:
`G:/TTMT/datn`

> Luu y: copy/chay tung lenh theo thu tu.

---

## 10 lenh demo

### (1)
```powershell
cd G:/TTMT/datn
```

### (2)
```powershell
docker compose up -d postgres
```

### (3)
```powershell
$env:PYTHONPATH="G:/TTMT/datn/apps/backend"
```

### (4)
```powershell
$env:APP_DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/vehicle_lpr"
```

### (5)
```powershell
$env:DATABASE_URL="postgresql://postgres:postgres@localhost:5432/vehicle_lpr"
```

### (6)
```powershell
python "G:/TTMT/datn/apps/backend/scripts/run_migrations.py"
```

### (7)
```powershell
python "G:/TTMT/datn/scripts/reset_seeded_test_state.py"
```

### (8)
```powershell
docker compose up -d --build backend
```

### (9)
```powershell
python "G:/TTMT/datn/scripts/test_seeded_flow.py" --base-url http://localhost:8000
```

### (10)
```powershell
curl http://localhost:8000/api/v1/import-batches/summary
```

---

## Ket qua ky vong de trinh bay

- Lenh (6): migration apply 001/002/003.
- Lenh (7): reset state thanh cong (fixture deterministic).
- Lenh (9): test suite pass `6/6` (`[OK] All tests passed!`).
- Lenh (10): API import summary tra ve JSON hop le.

---

## Bonus 1 lenh (neu can demo dashboard)

```powershell
cd G:/TTMT/datn/apps/dashboard; npm run dev
```

Mo URL Vite in ra (thuong `http://localhost:5173`) va vao section `Import Summary`.

---

## Neu loi nhanh (2 lenh chuan doan)

```powershell
docker compose logs backend --tail=120
curl http://localhost:8000/health
```
