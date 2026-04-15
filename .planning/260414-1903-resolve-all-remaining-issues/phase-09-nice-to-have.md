# Phase 09: Nice-to-have Improvements

**Ưu tiên**: 🟢 Thấp — làm nếu còn thời gian
**Trạng thái**: ⬜ Pending
**Ước tính**: ~5 giờ (tổng, chọn lọc)

---

## Danh sách cải tiến

### 9.1. Benchmark FPS: GPU vs CPU (~30 phút)
- Chạy E2E demo trên máy có GPU (nếu có)
- So sánh: CPU (1.6-2.1 FPS) vs GPU (kỳ vọng 10-15 FPS)
- Ghi kết quả vào báo cáo Ch.4
- **Lưu ý**: Cần máy có NVIDIA GPU + CUDA

### 9.2. Thêm video test đa dạng (~1 giờ)
- Tìm/quay thêm 2-3 video biển số VN thật
- Chạy E2E trên mỗi video, ghi kết quả
- Đánh giá: accuracy có thay đổi theo góc quay, ánh sáng, tốc độ xe?

### 9.3. Lưu ảnh minh chứng tốt hơn (~1 giờ)
- Ngoài crop biển số, lưu thêm full frame với annotation
- Format: `{timestamp}_{plate}_{trackid}_full.png` + `_crop.png`
- Phục vụ demo + báo cáo

### 9.4. WebSocket realtime push (~2 giờ)
- Thay polling bằng WebSocket trên dashboard
- Backend: FastAPI WebSocket endpoint
- Dashboard: `useWebSocket` hook
- **Phức tạp**: Cần handle reconnect, error states
- **Ý kiến**: Không cần thiết cho prototype, polling đủ dùng

### 9.5. Deduplicate events by plate_text (~30 phút)
- Hiện tại deduplicate bằng `(track_id, plate_text)` trong demo script
- Cần: deduplicate bằng `plate_text` thuần (bất kể track_id)
- Thêm time window: cùng biển số trong vòng 30s → coi là 1 event
- **Vị trí**: `apps/ai_engine/src/pipeline.py` hoặc `scripts/run-e2e-demo.py`

### 9.6. Deploy Docker lên VPS (~2 giờ)
- Push Docker images lên registry
- Deploy docker-compose lên VPS (DigitalOcean/Vultr)
- Configure domain + HTTPS
- **Chi phí**: ~$5-10/tháng

### 9.7. Quay video demo E2E chuyên nghiệp (~30 phút)
- Quay screen recording: terminal + dashboard đồng thời
- Voiceover giải thích từng bước
- 2-3 phút, resolution 1080p

---

## Đề xuất ưu tiên (nếu chỉ có 2-3 giờ)

1. **9.5 Deduplicate** — fix known issue, dễ làm, ảnh hưởng kết quả test
2. **9.1 Benchmark GPU** — số liệu tốt cho báo cáo (nếu có GPU)
3. **9.7 Video demo** — cần cho slide bảo vệ

---

## Tiêu chí hoàn thành

Mỗi item có tiêu chí riêng. Chọn items phù hợp với thời gian còn lại.
