# Test 6: Full OCR Evaluation — 3,731 ảnh VNLP

**Ngày**: 14/04/2026
**Script**: `scripts/eval-ocr-baseline.py`, `scripts/eval-with-postprocess.py`
**Dataset**: VNLP test split (3,731 ảnh từ `data/external/vnlp/VNLP_detection/`)
**Hardware**: NVIDIA GeForce GTX 1650 (4GB VRAM), CUDA, Python 3.11, PyTorch 2.11
**Models**: LP_detector.pt (YOLOv5, 41MB) + LP_ocr.pt (YOLOv5, 41MB)

---

## 1. Kết quả Baseline (không post-processing)

| Metric | 50 ảnh (cũ) | 3,731 ảnh (mới) |
|--------|------------|----------------|
| Detection rate | 96.0% (48/50) | **89.2%** (3,327/3,731) |
| Exact match | 33.3% (16/48) | **37.8%** (1,257/3,327) |
| Char accuracy | 51.0% | **53.8%** |
| Avg confidence | 0.82 | **0.835** |
| Throughput | 15.4 img/s | **14.7 img/s** (baseline), **16.6 img/s** (postprocess run) |
| Elapsed | ~3.2s | **253.6s** (baseline), **225.3s** (postprocess run) |

**Nhận xét**: Kết quả trên 3,731 ảnh **tốt hơn** baseline 50 ảnh:
- Exact match tăng 33.3% → 37.8% (+4.5%)
- Char accuracy tăng 51.0% → 53.8% (+2.8%)
- Detection rate giảm 96.0% → 89.2% (-6.8%) — do tập lớn hơn có nhiều ảnh khó

---

## 2. Kết quả Post-processing (char mapping + regex validate)

| Metric | Baseline | Post-processing | Thay đổi |
|--------|---------|----------------|---------|
| Exact match | 37.8% (1,257) | 32.7% (1,087) | **-5.1% ❌** |
| Char accuracy | 53.8% | 53.0% | **-0.8% ❌** |
| Valid VN format | 1,221 (36.7%) | 1,609 (48.4%) | **+11.7% ✅** |

### Kết quả: Post-processing làm GIẢM accuracy

---

## 3. Phân tích nguyên nhân

### 3.1. Two-letter series heuristic nhầm

Char mapping dùng heuristic: nếu plate có 9 ký tự HOẶC (8 ký tự VÀ vị trí 3 là chữ) → coi là biển 2 chữ cái (XX[AB]XXXXX).

**Ví dụ lỗi cụ thể**:
```
GT:   15B143850  (9 ký tự, 1-letter series: 15B + 143850)
Base: 15B143850  (OCR đọc ĐÚNG)
Post: 15BI43850  (char mapping sửa SAI: vị trí 3 '1'→'I' vì tưởng 2-letter series)
```

Heuristic nhầm vì plate 9 ký tự → auto assume 2-letter series → vị trí 3 phải là chữ → `1` bị map thành `I`.

### 3.2. Thống kê lỗi do char mapping

Từ 30 sample errors:
- **13/30** trường hợp: base đúng, post sửa sai (char mapping phá kết quả đúng)
- **12/30** trường hợp: cả base và post đều sai (OCR miss/thừa ký tự, mapping không giúp)
- **5/30** trường hợp: base sai, post cũng sai nhưng khác (mapping sửa nhưng không đúng GT)
- **0/30** trường hợp: base sai, post đúng (mapping không fix được case nào trong sample)

### 3.3. Tại sao valid format tăng nhưng accuracy giảm

Char mapping ép kết quả OCR về format biển VN hợp lệ (digit ở vị trí digit, letter ở vị trí letter). Điều này tăng tỉ lệ plate khớp regex pattern (+388 valid plates), nhưng trong nhiều trường hợp, ký tự gốc là đúng và bị sửa sai.

Nguyên nhân gốc: **OCR accuracy chưa đủ cao** để char mapping có hiệu quả. Khi OCR detect sai số lượng ký tự (thừa/thiếu), char mapping vẫn chạy trên chuỗi sai → sửa sai thêm.

---

## 4. Phân loại lỗi OCR (3,731 ảnh)

| Loại lỗi | Ví dụ | Tỉ lệ ước tính |
|----------|-------|----------------|
| Thiếu ký tự (OCR miss) | GT=36C07119, Pred=C07119 | ~35% |
| Thừa ký tự (false detect) | GT=34B259811, Pred=349BL259811 | ~15% |
| Nhầm ký tự hình dáng | GT=36C29764, Pred=36329764 (C→3) | ~25% |
| Biển không detect được | 404/3,731 = 10.8% | ~11% |
| Đúng hoàn toàn | 1,257/3,327 = 37.8% | ~34% |

---

## 5. Quyết định

**Tắt char mapping mặc định** (`ENABLE_CHAR_MAPPING=false` trong config.py).

Lý do:
- Post-processing giảm accuracy trên tập lớn (-5.1% exact match)
- Heuristic two-letter series không đủ robust
- Char mapping chỉ hữu ích khi OCR đọc đúng số ký tự → cần OCR accuracy cao hơn trước

**Giữ lại code + tests**: Char mapping và regex validate vẫn có trong codebase, có thể bật lại khi cải thiện OCR model.

**Giữ regex validate bật** (`ENABLE_PLATE_VALIDATION=true`): Chỉ validate format, không sửa ký tự → không ảnh hưởng accuracy.

---

## 6. Số liệu chính thức cho báo cáo

Sử dụng **kết quả baseline** (không post-processing) làm số liệu chính:

| Metric | Giá trị |
|--------|---------|
| Tập eval | 3,731 ảnh test (VNLP) |
| Plate detection rate | **89.2%** |
| OCR exact match | **37.8%** |
| OCR char accuracy | **53.8%** |
| Avg OCR confidence | **0.835** |
| Throughput (GPU) | **14.7-16.6 img/s** |
| Valid VN format (baseline) | **36.7%** (1,221/3,327) |

---

## 7. Hướng cải thiện (khuyến nghị)

1. **Padding crop biển số** trước khi OCR (thêm 10-15% border) → giảm miss ký tự ở rìa
2. **Confidence threshold filter**: chỉ apply char mapping khi confidence < threshold
3. **Majority voting**: nếu cùng biển số qua nhiều frame → chọn kết quả phổ biến nhất
4. **Fine-tune OCR model** trên VNLP dataset → tăng accuracy gốc trước khi post-process
5. **Length-based filter**: chỉ apply char mapping khi OCR output có đúng 7-9 ký tự VÀ khớp rough pattern

---

## Files tạo ra

- `data/processed/baseline_eval_results.json` — kết quả baseline 3,731 ảnh
- `data/processed/postprocess_eval_results.json` — kết quả so sánh baseline vs post-process
- `scripts/eval-with-postprocess.py` — script so sánh
- `test_plans_and_reports/test6-full-ocr-eval-3731.md` — report này
