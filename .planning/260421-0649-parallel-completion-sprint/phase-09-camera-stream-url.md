# Phase 09: Camera Stream URL Display

**Ưu tiên**: 🟢 Feature
**Branch**: `feat/stream-url`
**Worktree**: Main (sau Phase 05)
**Phụ thuộc**: Phase 05 (Dashboard ổn định)
**Ước tính**: 1-2 giờ

---

## Bối cảnh

Báo cáo mục 9.4 dự kiến: "Hiển thị stream URL camera trên dashboard để giám sát trực tiếp (việc thêm/sửa/xóa camera sẽ thực hiện trực tiếp trên database, không cần giao diện quản trị riêng)".

Bảng `cameras` trong DB đã có field `stream_url` (Text nullable).

---

## Yêu cầu

### 1. Backend: API endpoint list cameras

Check: endpoint `/api/v1/cameras` đã có chưa? Nếu chưa → thêm:

```python
# apps/backend/app/main.py
@app.get("/api/v1/cameras", response_model=List[CameraOut])
def list_cameras(db: Session = Depends(get_db)):
    return db.execute(select(Camera).order_by(Camera.created_at.desc())).scalars().all()
```

Schema `CameraOut` trong `schemas.py`:
```python
class CameraOut(BaseModel):
    id: str
    name: str
    gate_type: str  # student | staff
    location: str | None
    stream_url: str | None
    is_active: bool
    created_at: datetime
```

### 2. Frontend: Cameras section trên dashboard

Component mới: `apps/dashboard/src/components/CamerasSection.tsx`

```tsx
function CamerasSection() {
  const [cameras, setCameras] = useState<CameraOut[]>([]);
  
  useEffect(() => {
    fetchCameras().then(setCameras);
  }, []);
  
  return (
    <section>
      <h3>Cameras ({cameras.length})</h3>
      <table>
        <thead><tr><th>Name</th><th>Gate</th><th>Location</th><th>Stream</th><th>Active</th></tr></thead>
        <tbody>
          {cameras.map(c => (
            <tr key={c.id}>
              <td>{c.name}</td>
              <td>{c.gate_type}</td>
              <td>{c.location ?? '—'}</td>
              <td>
                {c.stream_url ? (
                  <a href={c.stream_url} target="_blank" rel="noopener noreferrer">
                    View stream
                  </a>
                ) : '—'}
              </td>
              <td>{c.is_active ? '✓' : '✗'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
```

### 3. Embed vào main.tsx

Thêm CamerasSection sau stats cards hoặc trong tab riêng.

### 4. API client

`apps/dashboard/src/api.ts`:
```typescript
export async function fetchCameras(): Promise<CameraOut[]> {
  const r = await fetch(`${BASE}/api/v1/cameras`);
  if (!r.ok) throw new Error(`Fetch cameras failed: ${r.status}`);
  return r.json();
}
```

`api-types.ts`:
```typescript
export interface CameraOut {
  id: string;
  name: string;
  gate_type: 'student' | 'staff';
  location: string | null;
  stream_url: string | null;
  is_active: boolean;
  created_at: string;
}
```

### 5. Test

- Seed 2 cameras: 1 có stream_url, 1 không
- Kiểm tra bảng hiển thị đúng
- Click "View stream" → mở tab mới (nếu URL hợp lệ)

---

## Files ownership

- `apps/backend/app/main.py` (thêm endpoint nếu chưa có)
- `apps/backend/app/schemas.py` (thêm CameraOut nếu chưa có)
- `apps/dashboard/src/api.ts` (thêm fetchCameras)
- `apps/dashboard/src/api-types.ts` (thêm CameraOut)
- `apps/dashboard/src/components/CamerasSection.tsx` (MỚI)
- `apps/dashboard/src/main.tsx` (embed)
- `apps/backend/tests/test_cameras_api.py` (MỚI)

---

## Tiêu chí thành công

- [ ] Endpoint `/api/v1/cameras` trả list cameras
- [ ] Dashboard hiển thị bảng cameras
- [ ] Stream URL là clickable link (mở tab mới)
- [ ] Backend test thêm ≥2 cases
- [ ] Responsive: bảng không vỡ trên mobile

---

## Rủi ro

- Thấp — thêm read-only endpoint, không sửa data
- Stream URL có thể invalid/private → hiển thị nhưng không play được (acceptable cho prototype)

---

## Output

- Branch `feat/stream-url` sẵn sàng merge
- 1 screenshot dashboard với cameras section
