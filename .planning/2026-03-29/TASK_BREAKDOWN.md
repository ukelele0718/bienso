# TASK BREAKDOWN
## Ke hoach theo ngay cho planning 2026-03-29

**Version**: 1.0  
**Ngay cap nhat**: 2026-03-29  
**Pham vi**: lap lich theo ngay cho lo trinh data -> train -> runtime -> backend -> dashboard  

---

## 0) Nguyen tac lap lich
- Uu tien duong critical path: `manifest -> annotation parser -> label QA -> smoke train -> full train`
- Cac cong doan train full nen duoc dat vao buoi toi / qua dem
- Ban ngay uu tien cac viec can nguoi ngoi may:
  - audit data
  - QA labels
  - sua parser
  - review metrics
  - fix bug integration
- Moi moc quan trong phai co artifact cu the, khong chi "da lam"

---

## 1) Cac moc bat buoc
- Moc 1: `dataset_manifest` canonical contract duoc chot
- Moc 2: `non-empty labels > 0`
- Moc 3: QA toi thieu 200 mau dat yeu cau
- Moc 4: smoke train detector chay het, khong OOM
- Moc 5: full train detector v1 co artifact duoc luu
- Moc 6: OCR baseline v1 co ket qua do duoc
- Moc 7: luong runtime 1 camera + backend + dashboard noi duoc voi nhau

---

## 2) Lich theo ngay

| Ngay | Muc tieu | Cong viec chinh | Dau ra bat buoc | Ghi chu |
| --- | --- | --- | --- | --- |
| Ngay 1 - 2026-03-29 | Chot scope va inventory review | Doc lai plan, chot scope 1 camera, chot danh sach file/thu muc data dang co, ghi bang inventory ban dau | Ban inventory nguon data, note trang thai repo, note cac risk data | Khong train ngay dau |
| Ngay 2 - 2026-03-30 | Chot contract du lieu | Chot `source_manifest`, `split_manifest`, chot convention label va OCR text | Van ban quy uoc data contract, ten file dich, structure folder dich | Day la diem chan lon nhat |
| Ngay 3 - 2026-03-31 | Audit annotation VNLP | Mo sample VNLP, doc annotation, liet ke edge case, xac dinh parser can viet gi | Note format VNLP + mapping field | Neu xong som, bat dau parser VNLP |
| Ngay 4 - 2026-04-01 | Audit annotation Kaggle/Roboflow | Giai nen cac goi can dung, doc sample annotation, quyet dinh active hay parked | Bang doi chieu `VNLP / Kaggle / Roboflow` | Neu 1 nguon qua lech, parked ngay |
| Ngay 5 - 2026-04-02 | Viet parser nguon chinh | Viet parser cho nguon active uu tien, output label test tren 100-300 file | Parser chay tren subset nho, co non-empty labels | Uu tien VNLP truoc |
| Ngay 6 - 2026-04-03 | Sua parser va convert lan 1 | Sua edge cases, chay convert lan 1 tren tap lon hon | Label tree lan 1, report so luong bbox / sample bi loi | Chua copy split lai neu parser chua on |
| Ngay 7 - 2026-04-04 | Chot parser nguon chinh | Chay convert full cho nguon chinh, verify `non-empty labels > 0` | Label tree full cho nguon chinh, report convert | Moc bat buoc dau tien |
| Ngay 8 - 2026-04-05 | Visual QA dot 1 | Kiem 200 mau random, danh dau cac loi nang, thong ke loi annotation | Bang QA dot 1, danh sach loi parser/label | Cong doan ton suc nhat |
| Ngay 9 - 2026-04-06 | Sua parser sau QA | Sua parser theo loi QA, regenerate labels neu can | Label tree lan 2 + changelog parser | Neu loi qua nhieu, doi lich smoke train 1 ngay |
| Ngay 10 - 2026-04-07 | Chot split train/val/test | Dedupe neu can, regen split, ghi seed va rule split | Split cuoi cung, split rule note, file count cuoi | Sau ngay nay khong doi split nua neu khong bat buoc |
| Ngay 11 - 2026-04-08 | Chuan bi smoke train | Tao config `yolov8n`, test dataloader, test batch, test VRAM | Cau hinh smoke train + log khong OOM | Chay buoi toi neu on |
| Ngay 12 - 2026-04-09 | Smoke train plate detector | Chay smoke train 10-15 epoch tren subset 5k-8k anh | Weights smoke, metrics, sample predictions | Qua dem neu can |
| Ngay 13 - 2026-04-10 | Doc metrics smoke train | Danh gia loss, val metric, prediction images, quyet dinh co full train ngay khong | Bao cao smoke train ngan + quyet dinh next step | Neu metric xau, quay lai QA labels |
| Ngay 14 - 2026-04-11 | Bat dau full train plate detector | Chay full train `yolov8n` epoch 50 | Run train full dang chay + log + artifact dir | Nen chay qua dem |
| Ngay 15 - 2026-04-12 | Theo doi full train + detect runtime scaffold | Theo doi nhiet do, VRAM, loss; dong thoi dung detect runtime scaffold | Metric trung gian + detect runtime scaffold | Day co the song song |
| Ngay 16 - 2026-04-13 | Hoan tat full train plate detector | Chot model plate detector v1 | `best.pt`, metrics, sample predictions | Moc quan trong |
| Ngay 17 - 2026-04-14 | Vehicle detector quyet dinh va smoke run | Quyet dinh co can fine-tune vehicle detector hay dung pretrained, neu can thi smoke run | Note quyet dinh + smoke vehicle artifact | Neu pretrained du, bo qua full train vehicle |
| Ngay 18 - 2026-04-15 | Chuan bi OCR baseline | Tao plate crop pipeline, tao OCR text labels, chon model OCR baseline | Tap crop + file text label OCR + config OCR | Khong train OCR neu crop con loang |
| Ngay 19 - 2026-04-16 | Smoke train OCR | Chay OCR baseline nho / fine-tune nhe | OCR smoke artifact + sample text predictions | Uu tien baseline nhanh |
| Ngay 20 - 2026-04-17 | OCR post-process | Them regex VN, char normalization, score threshold | Module post-process OCR + note loi pho bien | Day tang chat luong nhanh |
| Ngay 21 - 2026-04-18 | Tich hop detect + track + count | Noi detector, tracker, line/zone, debounce | Runtime module dem co ban | Chua can backend |
| Ngay 22 - 2026-04-19 | Tich hop plate detect + OCR runtime | Noi plate detector + crop + OCR + post-process | Runtime LPR module co ban | Test tren video file |
| Ngay 23 - 2026-04-20 | Noi backend event flow | Map payload runtime -> backend event, kiem tra luong account/transaction/barrier | Event flow chay duoc tu runtime sang backend | Tap trung dung contract |
| Ngay 24 - 2026-04-21 | Verify barrier va finance rules | Test case xe dang ky, xe la vao, xe tam ra | Bo test rule va checklist pass/fail | Neu can, sua backend ngay |
| Ngay 25 - 2026-04-22 | Dashboard operator flow | Hien thi realtime, tra cuu, event hold, verify flow | UI dashboard dung duoc cho demo | Khong can dep, can ro luong |
| Ngay 26 - 2026-04-23 | End-to-end test tren 2 kich ban cong | Chay luong file video / stream test, ghi metric counting/OCR/latency | Bao cao E2E dot 1 | Day la ngay rat quan trong |
| Ngay 27 - 2026-04-24 | Sua loi sau E2E | Sua bug lon, sua nguong, sua UX operator | Ban build on dinh hon + changelog fix | Neu phat sinh bug data, chi sua muc can thiet |
| Ngay 28 - 2026-04-25 | Chot demo prototype | Gom artifact, ghi KPI, chot checklist nghiem thu | Thu muc artifact demo, note KPI, note backlog | Khong them feature moi ngay cuoi |

---

## 3) Viec nen chay buoi toi / qua dem
- Convert full labels sau khi parser on
- Full train plate detector
- Full train vehicle detector neu can
- OCR fine-tune neu da co crop sach
- Copy split lon neu can duplicate dataset

---

## 4) Viec bat buoc lam ban ngay
- Audit annotation
- Visual QA labels
- Review sample predictions
- So sanh metrics giua cac run
- Sua parser / sua post-process / sua business rule

---

## 5) Nguong ra quyet dinh de khong mat thoi gian
- Neu sau Ngay 7 van `non-empty labels = 0`:
  - dung train
  - quay lai parser ngay lap tuc
- Neu sau Ngay 12 smoke train bi OOM:
  - giam `batch`
  - giam `imgsz`
  - giam `workers`
  - khong tiep tuc full train truoc khi smoke run dat
- Neu sau Ngay 13 prediction van vo ly:
  - quay lai QA labels
  - khong nhay vao full train
- Neu OCR baseline sau Ngay 20 van xau:
  - uu tien regex + char normalization truoc
  - khoan train OCR lon hon

---

## 6) Backlog neu con thoi gian
- Fine-tune vehicle detector rieng
- Them route/operator UX cho verify barrier dep hon
- Them benchmark so sanh `yolov8n` va `yolo11n`
- Them export report metric may doc duoc
- Them bo data low-light/glare rieng

---

## 7) Cach dung file nay
- Moi cuoi ngay:
  - danh dau ngay da xong / chua xong
  - ghi 3 dong:
    - da xong gi
    - vuong gi
    - ngay mai day viec gi
- Neu tre > 2 ngay o critical path:
  - bo bot scope phu
  - giu lai muc tieu: co label that -> co smoke train -> co full train v1
