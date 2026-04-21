# Test 19: Full Evaluation of Fine-tuned YOLOv8n LP Detector on 3,731 VNLP Test Images

**Date**: 2026-04-21  
**Engineer**: Agent B  
**Status**: COMPLETE

---

## 1. Mục tiêu

Validate kết quả fine-tuning `LP_detector_finetuned.pt` trên toàn bộ 3,731 ảnh test VNLP (thay vì 500 ảnh như trước). Kết quả này dùng làm **số liệu chính thức** trong đồ án tốt nghiệp.

---

## 2. Methodology

### Models

| Model | File | Architecture | Dataset trained on |
|-------|------|-------------|-------------------|
| Baseline LP Detector | `models/LP_detector.pt` | YOLOv5 (torch.hub) | Nguồn gốc ngoài VNLP |
| Fine-tuned LP Detector | `models/LP_detector_finetuned.pt` | YOLOv8n (ultralytics) | VNLP train split (29,837 ảnh) |
| OCR Model | `models/LP_ocr.pt` | YOLOv5 character detector | Giữ nguyên (không thay đổi) |

### Dataset

- **Split**: `test` (theo `data/processed/dataset_manifest.json`)
- **Số lượng**: 3,731 ảnh
- **Nguồn**: VNLP Detection dataset - biển số xe Việt Nam
- **Ground truth**: parse từ filename (pattern: `{idx}_{id}_{split}_{PLATE}_{x1}_{y1}_{x2}_{y2}.jpg`)

### Script

`scripts/eval-lp-detector-finetuned.py` — cùng script chạy cho cả hai detector.

- `--detector v5` cho baseline
- `--detector v8` cho fine-tuned

Script load OCR model một lần dùng chung. Pipeline: detect LP bbox → crop → OCR → normalize → compare với GT.

### OCR Pipeline (không thay đổi so với baseline)

1. Crop ảnh theo bbox từ detector
2. Chạy `LP_ocr.pt` → danh sách ký tự với tọa độ
3. Gap-based 2-row clustering (phát hiện biển 2 hàng)
4. Sắp xếp theo x_center trong mỗi hàng
5. Normalize: `re.sub(r"[^A-Za-z0-9]", "", text).upper()`
6. So sánh exact với GT (sau normalize)

OCR char mapping: TẮT (`ENABLE_CHAR_MAPPING=false` — không áp dụng trong script eval này).

### Hardware

- GPU: NVIDIA GeForce GTX 1650 (4GB VRAM)
- Python: 3.11.7, torch 2.11.0+cu128

### Log files

- `data/processed/eval-finetuned-3731.log` — output v8 full run
- `data/processed/eval-baseline-3731.log` — output v5 full run
- `data/processed/eval-finetuned-3731.json` — kết quả v8 JSON
- `data/processed/eval-baseline-3731.json` — kết quả v5 JSON (via same script)
- `data/processed/eval-finetuned-error-analysis.json` — phân tích lỗi 500 ảnh

---

## 3. Kết quả chính (3,731 ảnh)

### Bảng so sánh

| Metric | Baseline (YOLOv5 LP_detector) | Fine-tuned (YOLOv8n) | Delta |
|--------|-------------------------------|----------------------|-------|
| Tổng ảnh | 3,731 | 3,731 | — |
| Plates detected | 3,327 (89.2%) | 3,728 **(99.9%)** | +10.7pp |
| Exact match / detected | 1,257 / 3,327 (37.8%) | 2,562 / 3,728 **(68.7%)** | +30.9pp |
| Char accuracy | 53.8% | **82.4%** | +28.6pp |
| Avg OCR confidence | 0.835 | 0.844 | +0.009 |
| Throughput | 18.2 img/s | 17.9 img/s | -0.3 img/s |
| Elapsed | 204.5s | 208.3s | +3.8s |

> **Ghi chú**: Exact match rate tính trên số ảnh đã detect được (denominator = detected, không phải total). Nếu tính trên tổng ảnh: baseline = 33.7%, finetuned = 68.7% (do detection rate gần như 100%).

### Số liệu bổ sung

- **Missed detections** (finetuned): 3 ảnh (0.1%) — gần như hoàn hảo
- **Missed detections** (baseline): 404 ảnh (10.8%)
- **Tổng failures** (finetuned): 3,731 - 2,562 = 1,169 ảnh (bao gồm 3 không detect + 1,166 OCR sai)

---

## 4. So sánh với kết quả 500 ảnh trước đó

| Metric | 500 ảnh (trước) | 3,731 ảnh (mới) | Nhất quán? |
|--------|-----------------|-----------------|------------|
| Detection rate | 100.0% | 99.9% | ✓ (sai biệt 0.1%) |
| Exact match rate | 70.6% | 68.7% | ✓ (sai biệt 1.9pp) |
| Char accuracy | 83.8% | 82.4% | ✓ (sai biệt 1.4pp) |

**Nhận xét**: Kết quả trên 3,731 ảnh thấp hơn ~1-2pp so với 500 ảnh đầu. Điều này bình thường — 500 ảnh đầu thuộc phần dễ hơn của test set. Sai biệt nhỏ xác nhận kết quả **không bị overfitting trên sample nhỏ**.

---

## 5. Phân tích lỗi (Error Analysis)

Chạy trên 500 ảnh mẫu từ finetuned v8 — 353 đúng, 147 sai. Phân loại lỗi:

| Loại lỗi | Số lượng | Tỷ lệ | Mô tả |
|----------|----------|-------|-------|
| Wrong character | 122 | 83.0% | OCR đọc sai 1-2 ký tự (ví dụ: C→3, A→4) |
| Truncated / partial | 22 | 15.0% | OCR chỉ đọc được một phần biển số |
| Extra characters | 3 | 2.0% | OCR hallucinate thêm ký tự |
| No detection | 0 | 0.0% | Detector không bỏ sót (trong 500 mẫu) |

### Ví dụ lỗi phổ biến

**Wrong character (83%)** — lỗi chủ yếu từ OCR, không phải detector:
```
GT=36C29764  PRED=36329764   (C→3)
GT=36C26923  PRED=36326923   (C→3)
GT=36A12295  PRED=36A2295    (1 bị drop)
GT=36C27209  PRED=36C2209    (7 bị drop)
```

**Truncated (15%)** — OCR bỏ sót ký tự, đặc biệt khi ảnh nhỏ hoặc góc xấu:
```
GT=36R01219  PRED=601219     (3+R bị bỏ)
GT=29Z1413   PRED=Z1413      (29 bị bỏ)
GT=37C26050  PRED=372050     (C+6 bị bỏ)
GT=30M91151  PRED=3M1151     (0+9 bị bỏ)
```

**Extra chars (2%)** — OCR đọc thêm:
```
GT=34B259811  PRED=349B2L59811  (nhiễu)
GT=36B471648  PRED=36B4711648  (1 bị đọc đôi)
GT=29H111937  PRED=29NH111937  (N thêm vào)
```

### Kết luận phân tích lỗi

Phần lớn lỗi còn lại đến từ **OCR model** (`LP_ocr.pt`), không phải từ detector:
- C/3, A/4 confusion: OCR không distinguish được (đặc biệt biển mờ/nhỏ)
- Truncation ở đầu biển: thường xảy ra khi bbox của detector có margin trái/phải hẹp
- Fine-tuned detector đã giải quyết **hoàn toàn** vấn đề missed detection (10.8% → 0.1%)
- Bottleneck còn lại là **OCR accuracy**, không phải detection

---

## 6. Kết quả baseline đối chiếu chéo

Baseline đã được đánh giá qua hai scripts khác nhau cho kết quả giống nhau:

| Source | Images | Detected | Exact | Char acc |
|--------|--------|----------|-------|----------|
| `eval-ocr-baseline.py` (test12) | 3,731 | 89.2% | 37.8% | 53.8% |
| `eval-lp-detector-finetuned.py --detector v5` | 3,731 | 89.2% | 37.8% | 53.8% |

Kết quả **identical** — xác nhận tính nhất quán của evaluation methodology.

---

## 7. Khuyến nghị

**Dùng `LP_detector_finetuned.pt` làm detector mặc định** trong production pipeline.

Lý do:
1. Detection rate: 99.9% vs 89.2% (+10.7pp) — loại bỏ hầu hết missed detections
2. End-to-end exact match: 68.7% vs 37.8% (+30.9pp) — gần gấp đôi
3. Char accuracy: 82.4% vs 53.8% (+28.6pp)
4. Throughput tương đương: 17.9 vs 18.2 img/s (không ảnh hưởng đáng kể)
5. Kết quả nhất quán giữa 500 và 3,731 ảnh — không overfitting

Để cải thiện thêm cần tập trung vào **OCR model**:
- Fine-tune `LP_ocr.pt` trên VNLP để giảm C/3, A/4 confusion
- Hoặc áp dụng post-processing regex + char mapping có chọn lọc

---

## 8. Tóm tắt số liệu chính thức cho đồ án

| Hệ thống | Detection | Exact Match | Char Accuracy |
|----------|-----------|-------------|---------------|
| Baseline (LP_detector.pt + OCR) | 89.2% | 37.8% | 53.8% |
| **Fine-tuned (LP_detector_finetuned.pt + OCR)** | **99.9%** | **68.7%** | **82.4%** |
| Cải thiện | **+10.7pp** | **+30.9pp** | **+28.6pp** |

Dataset: VNLP test split — 3,731 ảnh. GPU: GTX 1650. Throughput: ~18 img/s.
