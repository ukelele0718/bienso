# Phase 02: PaddleOCR Alternative Experiment

**Ưu tiên**: 🟠 Experiment
**Branch**: `experiment/paddle-ocr`
**Worktree**: WT-B (isolation)
**Ước tính**: 2-3 giờ

---

## Bối cảnh

Research report [researcher-260421-ocr-library-comparison.md](../../plans/reports/researcher-260421-ocr-library-comparison.md) khuyến nghị PaddleOCR là lựa chọn tốt nhất:
- Speed: ~14-15 FPS GPU (tương đương YOLO hiện tại)
- Accuracy kỳ vọng: 95%+ (vs 37.8% hiện tại)
- Model nhỏ: 11.6-43 MB
- Cài đặt: `pip install paddleocr`

Đây là **experiment** để so sánh với YOLO char-level, KHÔNG phải thay thế luôn.

---

## Yêu cầu

### 1. Tạo PaddleOCR adapter

File mới: `apps/ai_engine/src/plate_ocr_paddle.py`

```python
from paddleocr import PaddleOCR
import numpy as np

class PlateOCRPaddle:
    def __init__(self, use_gpu: bool = False):
        self.ocr = PaddleOCR(use_angle_cls=False, lang='en', use_gpu=use_gpu)
    
    def read(self, plate_crop: np.ndarray) -> tuple[str | None, float]:
        result = self.ocr.ocr(plate_crop, cls=False)
        if not result or not result[0]:
            return None, 0.0
        # Join all detected text with descending confidence
        texts = []
        confs = []
        for line in result[0]:
            text, conf = line[1]
            texts.append(text)
            confs.append(conf)
        combined = ''.join(texts).upper()
        # Strip non-alphanumeric
        import re
        combined = re.sub(r'[^A-Z0-9]', '', combined)
        return combined, sum(confs) / len(confs) if confs else 0.0
```

Interface giống `PlateOCR` hiện tại → dễ swap trong pipeline.

### 2. Eval script

File mới: `scripts/eval-paddle-ocr.py`

Copy từ `scripts/eval-ocr-baseline.py`, thay `ocr_from_crop` bằng `PlateOCRPaddle`. Chạy trên cùng 3,731 test images để so sánh fair.

### 3. Benchmark

Chạy 3 configs:
- YOLO char-level (baseline): 14.7 img/s, 37.8% exact
- PaddleOCR CPU
- PaddleOCR GPU

Record: throughput, exact match, char accuracy, valid VN format rate.

### 4. Integration (nếu win)

Nếu PaddleOCR win: thêm config flag `OCR_BACKEND` = "yolo" | "paddle" trong `config.py`, pipeline chọn backend theo flag.

---

## Files ownership (tất cả trong worktree B)

- `apps/ai_engine/src/plate_ocr_paddle.py` (MỚI)
- `scripts/eval-paddle-ocr.py` (MỚI)
- `apps/ai_engine/src/config.py` (thêm OCR_BACKEND flag nếu integrate)
- `apps/ai_engine/src/pipeline.py` (chỉ sửa nếu integrate backend switch)
- Report: `test_plans_and_reports/test8-paddle-ocr-comparison.md`

---

## Tiêu chí thành công

| Metric | YOLO baseline | PaddleOCR target |
|--------|--------------|------------------|
| Exact match | 37.8% | ≥70% |
| Char accuracy | 53.8% | ≥85% |
| Throughput GPU | 14.7 img/s | ≥10 img/s (acceptable) |
| Throughput CPU | ~15 img/s | ≥3 img/s (acceptable) |

Nếu PaddleOCR đạt ≥70% exact match → strong recommendation merge.
Nếu < 60% → không merge, giữ YOLO.

---

## Rủi ro

- `paddlepaddle` package nặng (~200MB), conflict với PyTorch CUDA version
- GPU memory có thể không đủ (GTX 1650 4GB) nếu cả YOLO + Paddle cùng load
- License: Apache 2.0 (OK cho đồ án)
- `use_gpu=True` có thể crash nếu CUDA version mismatch → fallback CPU

---

## Output

- Report `test_plans_and_reports/test8-paddle-ocr-comparison.md`
- 2 JSON: `data/processed/paddle-ocr-cpu.json`, `data/processed/paddle-ocr-gpu.json`
- Bảng so sánh 3 configs
- Recommendation: merge hoặc không, kèm lý do
