# Phase 11: GPU Benchmark + Additional Test Videos

**Ưu tiên**: 🟢 Polish
**Branch**: main
**Worktree**: Main
**Phụ thuộc**: Phase 01 + 02 (OCR finalize)
**Ước tính**: 1-2 giờ

---

## Bối cảnh

Hiện tại chỉ có số liệu FPS trên CPU (1.6-2.1) và 1 video test biển VN. Báo cáo cần:
- Benchmark GPU vs CPU (đã có GTX 1650 → chạy được)
- Thêm 2-3 video test đa dạng để đánh giá robustness

---

## Phần A: GPU Benchmark

### Chuẩn bị

- Model đã support CUDA: YOLOv5 + YOLOv8 tự động detect `torch.cuda.is_available()`
- GPU: NVIDIA GTX 1650 4GB
- Cần force CUDA mode nếu chưa bật

### Tests

1. **Cold start**: load models → đo thời gian
2. **Single image inference**: 100 iterations → trung bình ms/inference
3. **Video processing**: 300 frames trungdinh22-demo.mp4 → FPS

### Script

File mới: `scripts/benchmark-gpu-vs-cpu.py`:

```python
import time
import torch

def benchmark_pipeline(video_path: str, device: str) -> dict:
    # Force device
    os.environ['CUDA_VISIBLE_DEVICES'] = '0' if device == 'cuda' else '-1'
    
    # Load pipeline
    pipeline = Pipeline()
    
    # Warmup 5 frames
    # ...
    
    # Benchmark 100 frames
    t0 = time.time()
    for i in range(100):
        pipeline.process_frame(frame, camera_id='bench', direction='in')
    elapsed = time.time() - t0
    
    return {
        'device': device,
        'total_frames': 100,
        'elapsed_s': elapsed,
        'fps': 100 / elapsed,
    }

cpu_result = benchmark_pipeline('trungdinh22-demo.mp4', 'cpu')
gpu_result = benchmark_pipeline('trungdinh22-demo.mp4', 'cuda')

print(f"CPU: {cpu_result['fps']:.1f} FPS")
print(f"GPU: {gpu_result['fps']:.1f} FPS")
print(f"Speedup: {gpu_result['fps'] / cpu_result['fps']:.1f}x")
```

### Expected results

- CPU: 1.6-2.1 FPS (đã biết)
- GPU: 10-20 FPS (kỳ vọng)
- Speedup: 5-10x

---

## Phần B: Thêm video test đa dạng

### Nguồn video

1. **Video biển số VN khác**: tìm trên YouTube (CC-BY hoặc fair use cho đồ án)
   - Keyword: "biển số xe Việt Nam cổng bãi đỗ"
   - Download bằng yt-dlp
2. **Video user tự quay**: dùng điện thoại, quay cảnh cổng trường ĐHBK (nếu có cơ hội)
3. **Scenario đa dạng**:
   - Ngày sáng
   - Hoàng hôn (ánh sáng thấp)
   - Mưa / trời ẩm (biển mờ)
   - Góc nghiêng
   - Nhiều xe cùng lúc

### Test matrix

| Video | Frames | Độ dài | Tình huống | Plates GT |
|-------|--------|--------|-----------|-----------|
| trungdinh22-demo.mp4 | 300 | 30s | Sáng, rõ nét | 2 |
| video-evening.mp4 | TBD | TBD | Hoàng hôn | TBD |
| video-rain.mp4 | TBD | TBD | Mưa | TBD |

### Eval

Chạy E2E demo trên mỗi video, record:
- Detection rate (biển detect được)
- OCR accuracy
- FPS
- Duplicate events
- Vehicle type mismatch

---

## Files ownership

- `scripts/benchmark-gpu-vs-cpu.py` (MỚI)
- `data/test-videos/*.mp4` (video mới, gitignored)
- Report: `test_plans_and_reports/test14-gpu-benchmark-multi-video.md`

---

## Tiêu chí thành công

- [ ] GPU speedup ≥3x so với CPU
- [ ] ≥2 video test thêm (ngoài trungdinh22)
- [ ] Báo cáo 2026-04-15 mục 5.2 update với số liệu mới
- [ ] Slide bảo vệ Slide 21 update với benchmark

---

## Rủi ro

- **TB**: CUDA version mismatch (PyTorch 2.11 + CUDA 12.8 hiện đã work → giữ nguyên)
- **Thấp**: Không tìm được video mới → chỉ quay 1 video thêm
- **TB**: GPU memory không đủ nếu batch size lớn → giữ batch=1

---

## Output

- Branch/commit trên main
- Report test14
- Update báo cáo + slide
