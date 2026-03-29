# Task checklist - VNLP seeded plates -> database -> backend -> dashboard

Ngay: 2026-03-29

## Chuan bi du lieu seed & schema
- [x] Xac dinh duoc rang filename VNLP chua chuoi bien so.
- [x] Xac dinh duoc rang `list_two_rows_label_xe_may.txt` co the dung de rut bien so ma khong can OCR.
- [x] Thong ke nhanh tap list: `5593` dong, `3227` bien so unique sau normalize upper-case.
- [x] Xac dinh schema hien tai da co `accounts`, `transactions`, `vehicle_events`, `plate_reads`, `barrier_actions`.
- [ ] Chot contract `registered_plates_seed.csv`.
- [ ] Chot rule normalize bien so duy nhat cho toan he thong.
- [ ] Chot policy dedupe khi cung 1 bien so xuat hien nhieu lan.

## Seed file va import policy
- [ ] Chot cac cot bat buoc: `plate_text`, `source`, `seed_group`.
- [ ] Chot cac cot nen co: `vehicle_type`, `note`.
- [ ] Quyet dinh import theo kieu `upsert` hay `skip-if-exists`.
- [ ] Quyet dinh import lai cung `seed_group` thi xu ly the nao.
- [ ] Quyet dinh account moi seed vao se co `registration_status=registered`.
- [ ] Quyet dinh account moi seed vao se co `balance_vnd=100000`.
- [ ] Quyet dinh co tao `init transaction` cho moi account moi hay khong.

## Logic nghiep vu barrier va registration
- [x] Xac dinh logic hien tai da co nhanh `registered + in`.
- [x] Xac dinh logic hien tai da co nhanh `temporary_registered + in`.
- [x] Xac dinh logic hien tai da co nhanh `temporary_registered + out`.
- [ ] Chot rule cho nhanh `registered + out`.
- [ ] Review lai y nghia `unknown` trong luong seed plates.
- [ ] Dam bao bien so trong seed khong bi tao lai thanh `temporary_registered`.
- [ ] Chot rule cho bien so khong co trong seed khi di vao cong.
- [ ] Chot rule cho bien so khong co trong seed khi di ra cong.

## Import script / admin flow
- [ ] Tao script import local cho `registered_plates_seed.csv`.
- [ ] Script phai normalize bien so truoc khi ghi DB.
- [ ] Script phai dedupe truoc khi import.
- [ ] Script phai sinh summary: `imported / skipped / invalid`.
- [ ] Script phai idempotent o muc toi thieu.
- [ ] Script phai tao `Account` moi cho plate chua ton tai.
- [ ] Script phai tao `Transaction(type='init')` cho account moi.
- [ ] Script phai bo qua hoac cap nhat hop ly neu account da ton tai.

## Backend API
- [ ] Them `GET /api/v1/accounts` co search + filter + pagination.
- [ ] Them `GET /api/v1/accounts/summary`.
- [ ] Xem xet `POST /api/v1/accounts/{plate}/mark-registered`.
- [ ] Xem xet `POST /api/v1/accounts/{plate}/adjust-balance`.
- [ ] Neu can, them API ho tro import preview hoac import summary.
- [ ] Dam bao `GET /api/v1/accounts/{plate_text}` van dung tot voi account seed.
- [ ] Dam bao `GET /api/v1/accounts/{plate_text}/transactions` hien dung `init transaction`.

## Backend test
- [ ] Test import plate moi -> tao account + init transaction.
- [ ] Test import duplicate -> khong tao duplicate account.
- [ ] Test event voi bien so trong seed, huong `in`.
- [ ] Test event voi bien so trong seed, huong `out`.
- [ ] Test event voi bien so ngoai seed, huong `in`.
- [ ] Test event voi bien so ngoai seed, huong `out`.
- [ ] Test verify hold van chay dung cho xe tam.

## Dashboard
- [ ] Them man hinh danh sach account / bien so.
- [ ] Them o search theo bien so.
- [ ] Them filter theo `registration_status`.
- [ ] Them trang chi tiet account.
- [ ] Hien so du hien tai.
- [ ] Hien lich su giao dich.
- [ ] Hien lich su event va barrier action lien quan.
- [ ] Them khu vuc verify queue cho cac barrier action dang hold.
- [ ] Them tong quan so luong `registered / temporary_registered / total`.

## Demo flow gia lap
- [ ] Chuan bi 1 tap plate da seed de demo.
- [ ] Chuan bi payload event gia lap cho plate da seed di `in`.
- [ ] Chuan bi payload event gia lap cho plate da seed di `out`.
- [ ] Chuan bi payload event gia lap cho plate chua seed di `in`.
- [ ] Chuan bi payload event gia lap cho plate tam di `out`.
- [ ] Xac nhan dashboard hien dung sau moi kich ban.

## Provenance va audit (de sau neu can)
- [ ] Can nhac them metadata import: `source`, `seed_group`, `imported_at`.
- [ ] Can nhac them lich su import batch.
- [ ] Can nhac them man hinh dashboard xem thong tin provenance.

## Kiem thu cuoi
- [ ] Import seed chay duoc tu dau den cuoi.
- [ ] Khong tao duplicate account khi import lai.
- [ ] Luong `registered` va `temporary_registered` phan biet ro rang.
- [ ] Barrier action phu hop rule da chot.
- [ ] Dashboard tra cuu va verify duoc.
- [ ] Co the demo luong nghiep vu ma khong can AI/OCR that.

