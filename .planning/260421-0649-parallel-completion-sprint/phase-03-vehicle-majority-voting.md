# Phase 03: Vehicle Type Majority Voting

**Ưu tiên**: 🟡 Improvement
**Branch**: `experiment/vehicle-voting`
**Worktree**: WT-C (isolation)
**Ước tính**: 1-2 giờ

---

## Bối cảnh

Hiện tại `_track_classes` tại [pipeline.py:101,160,217](../../apps/ai_engine/src/pipeline.py#L101) lưu class của track khi detect LẦN ĐẦU — không update sau đó.

Quan sát video trungdinh22-demo.mp4:
- track_8: biển 14K117970 — classify motorbike
- track_9: cùng biển 14K117970 — classify car ❌

Vấn đề: Khi xe biến mất rồi xuất hiện lại → SORT tạo track mới → YOLOv8 có thể classify khác (do góc/ánh sáng thay đổi).

---

## Giải pháp: Majority Voting

Thay vì lưu class đầu tiên, lưu **counter** của các class được detect trong suốt track:

```python
# pipeline.py
from collections import Counter

self._track_class_votes: dict[int, Counter] = {}  # track_id -> Counter({cls: count})

# Mỗi lần detect vehicle được gán track_id
def _update_track_class(self, track_id: int, cls_name: str):
    if track_id not in self._track_class_votes:
        self._track_class_votes[track_id] = Counter()
    self._track_class_votes[track_id][cls_name] += 1

def _get_vehicle_type(self, track_id: int) -> VehicleType:
    votes = self._track_class_votes.get(track_id)
    if not votes:
        return "car"
    most_common_cls = votes.most_common(1)[0][0]
    return _VEHICLE_TYPE_MAP.get(most_common_cls, "car")
```

---

## Yêu cầu

### 1. Sửa pipeline.py

- Thay `self._track_classes: dict[int, str]` → `self._track_class_votes: dict[int, Counter]`
- Update mỗi frame khi SORT match track với detection
- `_get_vehicle_type` đọc từ Counter

### 2. Ghi log decisions

Khi gửi event, log ra:
```
[track_5] plate=36H82613 classes_seen={car: 45, motorcycle: 3} → car (majority)
```

→ Giúp debug khi có mismatch.

### 3. Test

Chạy lại E2E trên trungdinh22-demo.mp4 (300 frames):
- So sánh kết quả trước/sau
- Mục tiêu: tất cả tracks của cùng plate có cùng vehicle_type

### 4. Unit test (mới)

Tạo `apps/ai_engine/tests/test_vehicle_type_voting.py` với các case:
- 1 track, 1 class → return class đó
- 1 track, nhiều class (car: 45, motorcycle: 3) → return "car"
- 1 track, tie (car: 5, motorcycle: 5) → return first most_common
- Track không tồn tại → return default "car"

---

## Files ownership (worktree C)

- `apps/ai_engine/src/pipeline.py` (sửa logic)
- `apps/ai_engine/tests/test_vehicle_type_voting.py` (MỚI)
- Report: `test_plans_and_reports/test9-vehicle-majority-voting.md`

---

## Tiêu chí thành công

- [ ] Unit tests pass (4+ cases)
- [ ] E2E test trên trungdinh22-demo.mp4: 0 mismatch vehicle_type cho cùng biển
- [ ] Performance không giảm (Counter update O(1))
- [ ] Log rõ ràng các votes cho mỗi decision

---

## Rủi ro

- Thấp — chỉ thay counter logic, không đổi interface
- Edge case: xe máy/ô tô bị nhầm class nhiều frames đầu → majority có thể vẫn sai nếu most frames sai

---

## Output

- PR/branch `experiment/vehicle-voting` sẵn sàng merge
- Report test so sánh trước/sau
- Nếu E2E test clean (0 mismatch) → merge ngay sau Batch 1
