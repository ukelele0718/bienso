# Chương 1: Cơ Sở Lý Thuyết

## 1.1. Đặt Vấn Đề và Tổng Quan Bài Toán

### 1.1.1. Bối Cảnh và Vấn Đề Thực Tế

Tại các cơ sở giáo dục đào tạo như Đại học Bách khoa Hà Nội, quản lý phương tiện ra vào khuôn viên là một nhiệm vụ hành chính quan trọng. Hiện nay, hầu hết các trường đại học lớn sử dụng phương pháp quản lý bán tự động: nhân viên bảo vệ ghi chép thủ công biển số xe khi xe vào/ra, rồi đối soát với hồ sơ đăng ký. Phương pháp này có những nhược điểm rõ rệt. Thứ nhất, khi lưu lượng xe cao (đặc biệt giờ cao điểm), việc ghi chép bị nhầm lẫn, ký tự khó đọc dẫn tới sai sót. Thứ hai, việc tra cứu lịch sử vào/ra mất thời gian, vì phải tìm kiếm thủ công trong các cuốn sổ hoặc file không có cấu trúc. Thứ ba, không thể cảnh báo khi phát hiện phương tiện lạ hoặc vi phạm quy định, vì quy trình kiểm tra được thực hiện sau, không thời gian thực.

Nhu cầu tự động hóa quy trình này là rõ ràng. Một hệ thống tự động có thể: (1) nhận diện biển số xe trong thời gian thực, (2) so khớp với cơ sở dữ liệu phương tiện được phép, (3) ghi nhận tự động lịch sử vào/ra với timestamp chính xác, (4) cảnh báo tức thời khi phát hiện bất thường. Đây chính là bài toán Automatic Number Plate Recognition (ANPR) - công nghệ nhận diện biển số xe tự động. ANPR không chỉ là một bài toán thị giác máy tính (computer vision), mà còn là một hệ thống tích hợp gồm camera, engine xử lý hình ảnh, backend dữ liệu, và giao diện người dùng.

### 1.1.2. Mục Tiêu và Phạm Vi của Đồ Án

Mục tiêu chính của đồ án này là thiết kế và xây dựng một prototype hệ thống quản lý phương tiện ra/vào dựa trên nhận diện biển số xe. Hệ thống này bao gồm ba thành phần chính: (1) **AI Engine** - xử lý video từ camera, phát hiện phương tiện, định vị và nhận diện biển số; (2) **Backend** - tiếp nhận sự kiện nhận diện từ AI Engine, quản lý dữ liệu phương tiện, xác thực quyền truy cập, và ghi nhận lịch sử; (3) **Dashboard** - giao diện web cho nhân viên bảo vệ/quản lý, hiển thị sự kiện real-time, cho phép tra cứu, kiểm tra, và xác nhận.

Về phạm vi, đồ án tập trung vào prototype với 1-2 camera đơn lẻ tại một cổng ra/vào, hỗ trợ cả xe máy và ô tô. Phạm vi không bao gồm: hệ thống phân tán với hàng chục camera (sẽ đòi hỏi kiến trúc RTSP streaming, load balancing), nhận dạng ngoại hình người lái (đòi hỏi thêm face recognition model), hoặc tích hợp với hệ thống bão hiểm bãi xe (parking management) toàn bộ. Thay vào đó, đồ án tập trung vào **độ chính xác OCR cao** trên biển số Việt Nam, **xử lý theo thời gian thực** với tốc độ frame cao, và **giao diện trực quan** cho người dùng cuối.

### 1.1.3. Lợi Ích và Ứng Dụng

Hệ thống ANPR tại cơ sở giáo dục mang lại nhiều lợi ích. Đối với nhân viên bảo vệ, công việc ghi chép thủ công được loại bỏ, thời gian kiểm tra rút ngắn, độ chính xác tăng lên. Đối với quản lý cơ sở, hệ thống cung cấp thống kê chi tiết: số lượng phương tiện vào/ra theo giờ, danh sách phương tiện bất thường, lịch sử di chuyển từng xe, hỗ trợ lập báo cáo an ninh. Ngoài ra, hệ thống còn có giá trị mở rộng: có thể nâng cấp để kiểm soát cổng tự động (barrier gate), tích hợp với hệ thống thanh toán bãi xe, hoặc kết nối với cơ quan công an để kiểm tra phương tiện không rõ nguồn gốc.

Về quy mô toàn cầu, thị trường ANPR đang phát triển nhanh chóng. Theo báo cáo của Fact MR năm 2024, thị trường ANPR toàn cầu có giá trị 4.14 tỷ USD năm 2025 và dự kiến đạt 9.27 tỷ USD năm 2034, với tốc độ tăng trưởng hàng năm (CAGR) là 9.36% [1]. Các ứng dụng chính bao gồm quản lý bãi xe thông minh (smart parking), trạm thu phí tự động (toll collection), hệ thống giao thông thông minh (ITS), và giám sát bảo mật công khai. Các quốc gia phát triển như Hoa Kỳ, Anh, Nhật Bản đã triển khai rộng rãi. Ở Việt Nam, ANPR vẫn là lĩnh vực mới, với dự án thí điểm tại một số cổng ra vào cơ sở công cộng và bãi xe tại TP. Hồ Chí Minh, Hà Nội.

[HÌNH 1.1: Sơ đồ quy trình quản lý phương tiện: (A) Phương pháp thủ công cũ (ghi chép bằng tay, mất thời gian, hay nhầm lẫn) → (B) Phương pháp tự động mới (camera → AI → backend → dashboard, thời gian thực)]

---

## 1.2. Tổng Quan về Công Nghệ Nhận Diện Biển Số Tự Động (ANPR/LPR)

### 1.2.1. Định Nghĩa và Cấu Trúc Hệ Thống

Automatic Number Plate Recognition (ANPR), còn gọi là License Plate Recognition (LPR), là một hệ thống nhúng xử lý thời gian thực, tự động phát hiện, trích xuất, và nhận dạng thông tin từ biển số phương tiện trong hình ảnh hoặc video [1]. Đây không phải là một công cụ độc lập, mà là một chuỗi các công đoạn xử lý hình ảnh kết hợp với nhận dạng ký tự.

Một hệ thống ANPR điển hình gồm bốn giai đoạn liên tiếp [2]:

1. **Phát Hiện Phương Tiện (Vehicle Detection)**: Từ frame hình ảnh, mô hình học sâu (thường là YOLO, Faster R-CNN) phát hiện vị trí tất cả các phương tiện (ô tô, xe máy). Đầu ra là danh sách các bounding box với tọa độ (x, y, width, height).

2. **Định Vị Vùng Biển Số (Plate Localization)**: Trong vùng mỗi phương tiện, hệ thống xác định vị trí chính xác của biển số. Đây có thể dùng mô hình YOLO riêng hoặc heuristic dựa trên màu sắc và kết cấu (vùng phản quang, có đường viền).

3. **Phân Đoạn Ký Tự (Character Segmentation)**: Biển số được chia thành các vùng con, mỗi vùng tương ứng với một ký tự (chữ cái hoặc chữ số). Bước này quan trọng vì biển 2 hàng hoặc biển bẩn có thể gây khó khăn.

4. **Nhận Dạng Ký Tự (OCR)**: Mỗi ký tự được đưa vào mô hình OCR (có thể dùng CNN + CTC, CRNN, hoặc LPRNet) để xác định giá trị của nó. Kết quả cuối cùng là chuỗi ký tự đầy đủ, ví dụ "30-AB-12345".

Hiệp thương tế giữa các giai đoạn này là rất quan trọng: lỗi ở bước detection sẽ dẫn tới bỏ sót các biển, lỗi ở localization sẽ cắt biển không đúng, và lỗi ở OCR sẽ cho kết quả nhầm lẫn ký tự.

### 1.2.2. Tiến Hóa Công Nghệ ANPR

Nghiên cứu ANPR đã phát triển qua ba thế hệ chính [1]:

**Thế hệ 1: Xử Lý Hình Ảnh Truyền Thống (2000-2010).** Phương pháp này dựa trên các kỹ thuật xử lý hình ảnh cơ bản: phát hiện cạnh (edge detection), phân tích kết cấu, phân ngưỡng (thresholding) để tách vùng màu biển. Ưu điểm là nhanh và không đòi hỏi tập dữ liệu lớn. Nhược điểm là khó bền vững trước các biến động của ánh sáng, góc chụp, hoặc tình trạng biển bẩn/cũ. Hơn nữa, nhận dạng ký tự dựa trên template matching hoặc máy học cổ điển (SVM) có độ chính xác thấp.

**Thế hệ 2: Học Sâu Đa Giai Đoạn (2015-2020).** Sự xuất hiện của deep learning (CNN, RNN) cho phép xây dựng các mô hình riêng cho mỗi giai đoạn, được huấn luyện trên tập dữ liệu lớn. Ví dụ: Faster R-CNN cho vehicle detection, mô hình YOLO hoặc SSD cho plate localization, CRNN + CTC cho OCR. Mỗi mô hình được tối ưu hóa riêng, cho độ chính xác cao hơn. Tuy nhiên, phương pháp này yêu cầu huấn luyện và điều chỉnh nhiều mô hình, tốc độ tổng hợp có thể chậm.

**Thế hệ 3: End-to-End Neural Networks (2020-nay).** Các mô hình mới cố gắng học toàn bộ quy trình từ ảnh thô đến kết quả biển số trong một mô hình duy nhất, hoặc giảm số lượng mô hình xuống 2-3 thành phần. Lợi ích là tối ưu hóa toàn cục, giảm độ trễ tích lũy, và dễ triển khai. Các công bố gần đây tập trung vào việc cải tiến end-to-end recognition models và tăng tốc độ xử lý.

### 1.2.3. Thách Thức Chính của ANPR

Dù công nghệ đã tiến bộ, ANPR vẫn gặp phải nhiều thách thức [2]:

- **Điều Kiện Ánh Sáng Thay Đổi (Lighting Variations)**: Ảnh chụp vào buổi sáng với ánh sáng mạnh, buổi tối với ánh đèn kém, hoặc trời mây che phủ, đều ảnh hưởng tới chất lượng hình ảnh, độ tương phản của biển số, và độ phản quang.

- **Góc Chụp Không Ổn Định (Viewing Angles)**: Nếu camera không đặt vuông góc với xe, biển sẽ bị méo, ký tự bị nén hoặc giãn, gây khó khăn cho OCR. Góc lệch >30° có thể làm sai lệch kết quả.

- **Vật Cản Che Khuất (Occlusion)**: Phần biển bị che bởi xe khác, bụi bẩn, bùn, hoặc hư hỏng, dẫn tới mất mát thông tin ký tự.

- **Mờ Chuyển Động (Motion Blur)**: Xe di chuyển nhanh khi quay frame, làm biển bị mờ, ký tự không rõ ràng, độ chính xác OCR giảm.

- **Biển Số Nhiều Hàng (Multi-row Plates)**: Một số phương tiện (xe máy, xe tải nhỏ) sử dụng biển 2 hàng, nơi mã tỉnh + chữ cái ở hàng 1, chữ số ở hàng 2. Việc phân đoạn và sắp xếp lại ký tự theo đúng thứ tự là phức tạp.

Các hệ thống commercial (ví dụ: Hikvision, Dahua) đã tối ưu hóa để đối mặt với các thách thức này thông qua pre-processing, augmentation dữ liệu, và ensemble models. Tuy nhiên, mỗi khu vực địa lý (quốc gia, thậm chí tỉnh) có những đặc tính khác nhau (format biển, loại phương tiện, điều kiện ghi), nên mô hình cần được fine-tune cụ thể.

[HÌNH 1.2: So sánh ba thế hệ công nghệ ANPR - (A) Traditional: edge detection + template matching (nhanh nhưng kém chính xác); (B) Deep Learning multi-stage: mô hình riêng cho mỗi giai đoạn (chính xác cao nhưng phức tạp); (C) End-to-end: một hoặc vài mô hình (cân bằng tốc độ - chính xác)]

---

## 1.3. Công Nghệ YOLO: Phát Hiện Đối Tượng Theo Thời Gian Thực

### 1.3.1. Kiến Trúc và Nguyên Lý YOLO

YOLO (You Only Look Once) là họ mô hình phát hiện đối tượng (object detection) được giới thiệu bởi Redmon et al. năm 2016 [4], [5]. Khác với các phương pháp hai giai đoạn (two-stage detectors) như Faster R-CNN, YOLO là một detector một giai đoạn (single-shot detector): chia hình ảnh thành lưới (grid), và từ mỗi ô lưới, dự đoán thẳng bounding box của vật thể và lớp (class) của nó. Ưu điểm là tốc độ rất nhanh, phù hợp cho ứng dụng real-time.

Nguyên lý hoạt động: đầu vào là ảnh 416×416 (hoặc 640×640 tùy phiên bản). Backbone CNN trích xuất các đặc trưng (features). Các đặc trưng này được đưa vào cổ cây (neck) - một chuỗi các lớp kết hợp, thường sử dụng Feature Pyramid Network (FPN) để đa tỷ lệ. Cuối cùng, head (đầu) dự đoán: (1) điểm tin cậy (objectness score) cho mỗi ô lưới, (2) bounding box (x, y, width, height), (3) xác suất class cho mỗi lớp.

Từ lịch sử phát triển, YOLO đã trải qua nhiều phiên bản:
- **YOLOv1 (2016)**: Mô hình gốc, mạnh lên 98 lớp.
- **YOLOv3 (2018)**: Cải tiến backbone (Darknet-53), dự đoán đa tỷ lệ, 80 lớp COCO.
- **YOLOv4 (2020)**: Các cải tiến training (Data Augmentation, BoS - Bag of Freebies, BoA - Bag of Specials).
- **YOLOv5 (2020)**: Tối ưu hóa mã nguồn, nhanh hơn, still sử dụng anchor boxes.
- **YOLOv8 (2023)**: Loại bỏ anchor boxes, sử dụng anchor-free head, độ chính xác cao hơn, tốc độ nhanh hơn [4].

### 1.3.2. YOLOv8 Nano: Phiên Bản Siêu Nhẹ

Để phục vụ ứng dụng edge (thiết bị giới hạn tài nguyên như camera IP, Jetson Nano), Ultralytics đã phát hành các phiên bản lightweight của YOLOv8. **YOLOv8 Nano (YOLOv8n)** là phiên bản nhỏ nhất [4], [6]:

- **Số tham số**: 3.2 triệu (so với 25.9M của YOLOv8s, 68M của YOLOv8m)
- **GFLOPs**: 8.7 (ở đầu vào 640×640), tức là chỉ cần ~1/100 tính toán so với mô hình lớn
- **mAP trên COCO**: 37.3% (thấp hơn YOLOv8s 44.9%, nhưng vẫn chấp nhận được cho ứng dụng real-time)
- **Tốc độ**: 0.99 ms trên GPU A100 với TensorRT, có thể chạy ở 100+ FPS
- **Kiến trúc**: CSP backbone (Darknet với Cross Stage Partial), PAN-FPN neck, anchor-free head. Độ sâu (depth) và chiều rộng (width) bị giảm 33% và 25% so với YOLOv8s

YOLOv8n rất phù hợp cho ứng dụng phát hiện phương tiện tại cơ sở giáo dục, vì quant vùng được giới hạn, lưu lượng xe không cao như cổng quốc lộ, mà chủ yếu cần tốc độ và độ chính xác khá.

### 1.3.3. Ứng Dụng YOLO cho Phát Hiện Ký Tự trong OCR

Ngoài phát hiện phương tiện, YOLO còn có thể được sử dụng để phát hiện **từng ký tự riêng lẻ** trên biển số [4], [7]. Phương pháp này khác với segmentation: thay vì phân tách ảnh thành các vùng đơn sắc, ta huấn luyện một mô hình YOLO để nhận ra 36 lớp (26 chữ cái A-Z + 10 chữ số 0-9), và mô hình sẽ phát hiện bounding box của mỗi ký tự.

Lợi ích của cách tiếp cận này: (1) không cần bước phân đoạn thủ công, (2) có thể xử lý biển bẩn, méo, hoặc chuyển động, vì YOLO bền vững hơn template matching, (3) kết hợp với Optical Character Recognition (OCR) truyền thống hoặc OCR bằng CNN, mô hình có thể đạt độ chính xác cao. Tuy nhiên, nhược điểm là cần tập dữ liệu với annotation ký tự riêng lẻ, công việc annotation thủ công rất tốn kém.

### 1.3.4. So Sánh YOLO với Các Detector Khác

[BẢNG 1.1: So sánh các mô hình phát hiện đối tượng]

| Mô hình | Kiểu | mAP COCO | Tốc độ (ms) | Tham số | Ứng dụng |
|--------|------|----------|-----------|--------|---------|
| Faster R-CNN | Two-stage | 42.7% | 140 | 41.8M | Chính xác cao, tốc độ thấp |
| SSD300 | One-stage | 41.4% | 20 | 26.3M | Cân bằng |
| YOLOv5s | One-stage | 43.0% | 3.2 | 7.2M | Real-time |
| YOLOv8n | One-stage | 37.3% | 0.99 | 3.2M | Ultra-lightweight |
| YOLOv8m | One-stage | 50.2% | 3.8 | 25.9M | Chính xác cao + nhanh |

Như bảng trên, YOLOv8n là lựa chọn tối ưu cho edge deployment (tốc độ vs tham số tối thiểu), trong khi YOLOv8m phù hợp cho server backend (mAP cao). Ứng dụng ANPR tại cơ sở giáo dục, nếu có server mạnh, có thể sử dụng YOLOv8m để tăng độ chính xác phát hiện phương tiện dưới các điều kiện kém (đêm, trời mưa).

[HÌNH 1.3: Tiến hóa YOLO từ v1 → v8 - Biến đổi từ anchor-based (v5) sang anchor-free (v8), giảm độ phức tạp, tăng tốc độ NMS]

---

## 1.4. Theo Dõi Đa Đối Tượng Theo Thời Gian Thực với SORT

### 1.4.1. Bài Toán Theo Dõi Đa Đối Tượng (Multi-Object Tracking)

Khi xử lý video từ camera, mỗi frame được phát hiện các phương tiện độc lập. Tuy nhiên, để quản lý từng phương tiện, cần biết **danh tính của nó qua các frame liên tiếp** - đây là bài toán **Multi-Object Tracking (MOT)**. Ví dụ, nếu một xe vào vào khung hình từ trái sang phải, cần ghi nhận rằng "xe ID=5 ở frame 10" và "xe ID=5 ở frame 11" là **cùng một chiếc xe**, không phải hai xe khác nhau.

Bài toán MOT bao gồm: (1) **Detection**: phát hiện vị trí vật thể ở mỗi frame (đã có YOLOv8), (2) **Association**: quyết định detection nào ở frame t ứng với track nào từ frame t-1, (3) **State Management**: cập nhật vị trí, vận tốc, và trạng thái của mỗi track (còn tồn tại, bị mất, hoặc kết thúc).

Giải pháp hiếu ứng nhất là kết hợp Kalman Filter (dự báo vị trí tiếp theo) với Hungarian Algorithm (tối ưu hóa phép gán detection-to-track). Đây chính là nguyên lý của SORT.

### 1.4.2. SORT: Mô Hình Kalman và Hungarian Assignment

SORT (Simple Online and Realtime Tracking) được Bewley et al. giới thiệu năm 2016 tại IEEE ICIP [8], [9]. Thuật toán này rất thanh lịch:

**Bước 1: State Representation.** Mỗi vật thể theo dõi được biểu diễn bằng vector trạng thái 7 chiều:
- (x, y) = tọa độ tâm bounding box
- s = diện tích (scale) của bounding box
- r = tỉ lệ chiều rộng/chiều cao (aspect ratio)
- (vx, vy, vs) = vận tốc tương ứng của các thành phần trên

Mô hình động được giả định là **constant velocity model**: vị trí mới = vị trí cũ + vận tốc × Δt. Đây là giả định hợp lý cho các vật thể chuyển động với vận tốc gần như hằng số trong khoảng thời gian ngắn (một vài frame).

**Bước 2: Prediction (Dự báo).** Sử dụng **Kalman Filter**, từ trạng thái ở frame t-1, dự báo trạng thái ở frame t. Kalman Filter bao gồm hai pha:
- *Predict*: Tính toán ước lượng tiên nghiệm (prior estimate) và ma trận hiệp phương sai lỗi dự báo.
- *Update*: Khi mới có phép đo (detection) từ frame t, cập nhật ước lượng hậu nghiệm (posterior estimate) bằng cân nặng giữa dự báo và phép đo.

Kalman Filter tối ưu theo nguyên lý bình phương tối thiểu, giả định tiếng ồn là Gaussian. Nó cho phép hệ thống **khoan dung với thiếu detection** (nếu frame t không phát hiện vật thể, track vẫn được duy trì bằng dự báo), và **tự động bỏ qua detection sai** (outliers).

**Bước 3: Association (Phối hợp).** Sau khi dự báo, cần gán các detection từ frame t với các tracks dự báo từ frame t-1. Để làm điều này:
1. Tính ma trận **Intersection-over-Union (IoU)** giữa mỗi detection và mỗi predicted bounding box. IoU = (diện tích giao) / (diện tích hợp), giá trị từ 0 (không trùng) đến 1 (trùng hoàn toàn).
2. Chuyển IoU thành **cost matrix** (chi phí = 1 - IoU).
3. Giải bài toán **optimal assignment** bằng **Hungarian Algorithm**, cổ điển từ combinatorial optimization. Thuật toán này tìm phép gán một-một giữa detection và track sao cho tổng chi phí minimal, độ phức tạp O(n³).
4. Các detection được gán (cost < ngưỡng) được cập nhật track tương ứng. Detection không được gán tạo track mới. Track không được gán là "missing" - nếu không được gắn lại trong vài frame liên tiếp (thường 30 frame), sẽ bị loại bỏ.

### 1.4.3. Hiệu Suất và So Sánh với Các Tracker Khác

SORT có những đặc điểm nổi bật [8], [9], [11]:

- **Tốc độ Cực Nhanh**: 260 Hz (60 fps video, xử lý 4 frame cùng lúc) - nhanh hơn 20× so với các tracker khác thời kỳ 2016.
- **Đơn Giản**: Không cần CNN backbone hoặc deep appearance feature, chỉ dùng hình học (IoU) và Kalman Filter. Code Python tinh gọn, dễ hiểu, dễ sửa.
- **Không Cần Training**: Kalman Filter là phương pháp thống kê, không cần huấn luyện trên dữ liệu.

Tuy nhiên, SORT có nhược điểm: **ID Switch** - khi hai vật thể xuyên qua nhau hoặc quay lại, nó có thể bị nhầm lẫn danh tính. Các phương pháp nâng cao như **DeepSORT** (2017) [9] giải quyết vấn đề này bằng cách thêm CNN trích xuất **deep appearance feature** - một embedding vector 128 chiều mô tả hình dáng/màu sắc của vật thể. Trong phối hợp, không chỉ dùng IoU, mà cân nhân thêm khoảng cách feature. Tuy nhiên, DeepSORT chậm hơn (30-40 Hz).

Gần đây, **ByteTrack** (2021) [10] đã đề xuất chiến lược phối hợp hai giai đoạn: trước tiên gắn tất cả các detection có confidence cao, sau đó recover detection confidence thấp bằng cách kiểm tra xem nó có gần track nào không. Cách này giảm ID switch mà vẫn giữ tốc độ cao (>100 Hz), đạt MOTA 77.3% trên tập benchmark MOT17.

Cho ứng dụng ANPR tại cơ sở giáo dục, SORT là lựa chọn lý tưởng, vì: (1) lưu lượng xe không quá dày đặc (không có nhiều xuyên qua), (2) tốc độ xử lý yêu cầu <100 FPS, (3) triển khai đơn giản, (4) nếu cần cải tiến, có thể nâng cấp lên ByteTrack mà không thay đổi toàn bộ kiến trúc.

[BẢNG 1.2: So sánh ba thuật toán theo dõi]

| Tracker | Giai đoạn | Độ Phức Tạp | Tốc độ (Hz) | MOTA | ID Switch | Ứng dụng |
|---------|-----------|-----------|----------|------|-----------|---------|
| SORT | Kalman + Hungarian | O(n³) | 260 | - | Cao | Real-time, mật độ thấp |
| DeepSORT | + CNN Feature | O(n²×m) | 30-40 | - | Thấp | Chính xác cao, tốc độ thứ cấp |
| ByteTrack | Two-stage matching | O(n×m) | >100 | 77.3% | Trung bình | Cân bằng tốt |

[HÌNH 1.4: Quy trình SORT ở mỗi frame - (1) Kalman Predict: dự báo vị trí track từ frame t-1; (2) Detection: phát hiện phương tiện ở frame t; (3) Association: tính IoU matrix, Hungarian solver tìm phép gán tối ưu; (4) Update: Kalman update trạng thái; (5) Manage: tạo/xóa track]

---

## 1.5. Công Nghệ Web cho Hệ Thống Giám Sát Khuôn Viên

### 1.5.1. Backend Web: FastAPI

Để tiếp nhận sự kiện nhận diện từ AI Engine (mỗi phương tiện được nhận diện là một sự kiện), xử lý logic, và cung cấp API cho dashboard, cần một framework web hiệu suất cao. **FastAPI** [15] là lựa chọn tối ưu cho ứng dụng này.

FastAPI là một framework web hiện đại cho Python, ra mắt năm 2018 bởi Sebastián Ramírez. Những ưu điểm chính:

- **Hiệu Suất Async**: Sử dụng `async/await` của Python, cho phép xử lý hàng trăm request đồng thời mà không cần threading hoặc multiprocessing phức tạp.
- **Validation Tự Động bằng Pydantic**: Khi một request gửi đến, FastAPI tự động kiểm tra dữ liệu khớp với schema được định nghĩa. Nếu sai, trả về lỗi 422 với chi tiết.
- **OpenAPI/Swagger Docs Tự Động**: Từ code, FastAPI tự sinh file `openapi.json` và giao diện Swagger UI tương tác, rất tiện lợi cho developer.
- **Tích Hợp SQLAlchemy ORM**: Kết nối Database dễ dàng, quản lý session, transaction một cách sạch sẽ.

Ứng dụng tại cơ sở giáo dục, FastAPI sẽ:
1. Tiếp nhận POST request từ AI Engine, chứa thông tin biển số nhận diện, timestamp, confidence score.
2. Thực hiện logic barrier rule: check biển số có trong danh sách phương tiện được phép không, nếu không tạo account tạm thời.
3. Lưu event vào cơ sở dữ liệu.
4. Broadcast event tới dashboard qua WebSocket (real-time push).
5. Cung cấp REST API cho dashboard để tra cứu sự kiện, tài khoản, phương tiện.

Tốc độ xử lý kỳ vọng: mỗi request nhận diện ~50ms (bao gồm logic, database insert), có thể xử lý 20 request/giây (tương ứng 20 phương tiện/giây qua cổng, nằm trong dự tính).

### 1.5.2. Cơ Sở Dữ Liệu: PostgreSQL

Để lưu trữ dữ liệu và hỗ trợ tra cứu, sử dụng **PostgreSQL** [16] - cơ sở dữ liệu quan hệ mở rộng mạnh nhất hiện nay.

Schema cơ bản của hệ thống:

| Bảng | Mục Đích |
|------|---------|
| `vehicles` | Danh sách phương tiện đăng ký (id, plate_number, owner, status) |
| `events` | Lịch sử sự kiện vào/ra (id, vehicle_id, timestamp, confidence, gate_type) |
| `license_plate_reads` | Kết quả OCR chi tiết (id, event_id, plate_text, char_scores[]) |
| `cameras` | Thông tin camera (id, location, direction, ip_address) |
| `users` | Tài khoản nhân viên bảo vệ/quản lý (id, name, role, password_hash) |
| `accounts` | Tài khoản phương tiện tạm (id, plate_number, balance, created_at, expires_at) |

PostgreSQL có nhiều ưu điểm:
- **ACID Compliance**: Đảm bảo tính toàn vẹn dữ liệu, ngay cả khi server bị dừng đột ngột.
- **JSON Support**: Cột có thể lưu JSON, ví dụ mảng độ tin cậy từng ký tự OCR.
- **Indexes**: Tạo B-tree index trên `plate_number`, `timestamp` để tra cứu nhanh.
- **Scalability**: Hỗ trợ partitioning bảng lớn (ví dụ: bảng `events` partition theo tháng), replication cho high availability.

Ứng dụng tại cơ sở giáo dục, PostgreSQL được chạy trong một container Docker, tách biệt khỏi FastAPI backend. Dữ liệu được backup định kỳ.

### 1.5.3. Frontend Web: React + TypeScript

Dashboard của hệ thống là giao diện web cho nhân viên bảo vệ/quản lý. Sử dụng **React** [19] kết hợp **TypeScript** để đảm bảo type-safety.

Các thành phần chính của dashboard:

1. **Live Counter**: Hiển thị số phương tiện vào/ra trong hôm nay, real-time cập nhật qua WebSocket.
2. **Recent Events Table**: Bảng danh sách các sự kiện mới nhất, hiển thị biển số, thời gian, gate (vào/ra), trạng thái xác nhận.
3. **Verify Queue**: Hàng đợi những sự kiện cần xác nhận thủ công (ví dụ: biển số không rõ, confidence thấp). Nhân viên có thể click để xem ảnh snapshot biển số, confirm hoặc reject.
4. **Search & Filter**: Tra cứu sự kiện theo ngày, biển số, gate, trạng thái.
5. **Statistics Chart**: Biểu đồ lưu lượng xe theo giờ (ở định vị nào, vào bao nhiêu, ra bao nhiêu).

React được chọn vì:
- **Component-Based**: Mỗi thành phần (counter, table, chart) là một component độc lập, tái sử dụng được.
- **TypeScript**: Bắt lỗi type tại compile time, giảm bug runtime.
- **Rich Ecosystem**: Thư viện cho chart (Recharts, Chart.js), table (TanStack, AG Grid), form validation rất phong phú.
- **Real-time Support**: WebSocket library (socket.io) tích hợp dễ dàng để nhận real-time event từ backend.

### 1.5.4. Containerization: Docker

Để dễ triển khai và tái sản xuất môi trường, toàn bộ hệ thống được đóng gói thành Docker containers [19]:

```
docker-compose.yml:
  - ai-engine: Service xử lý video (tùy chọn, có thể chạy riêng trên GPU machine)
  - fastapi-backend: Container chứa FastAPI app
  - postgresql-db: Container chứa PostgreSQL
  - react-dashboard: Container chứa React app (Nginx serve static)
```

Lợi ích:
- **Isolation**: Mỗi service có dependency riêng, không xung đột.
- **Portability**: Chạy trên laptop dev, cloud server, hoặc Kubernetes cluster mà không cần thay đổi code.
- **Scaling**: Dễ dàng spin up nhiều backend instances, load balance, auto-restart nếu crash.

---

## 1.6. Đặc Tính Biển Số Xe Việt Nam

### 1.6.1. Khung Pháp Lý và Định Dạng

Theo **Thông Tư 24/2023/TT-BCA** (hiệu lực từ 15 tháng 8 năm 2023) của Bộ Công An Việt Nam [12], biển số xe phải tuân theo chuẩn mới. Thông Tư này thay thế Thông Tư 58/2020/TT-BGTVT, chủ yếu bổ sung quy định quản lý kỹ thuật an ninh, tính xác thực của biển, và quy trình cấp phát.

**Định dạng biển số Việt Nam:**

Tiêu chuẩn gồm ba thành phần:
1. **Mã Tỉnh** (2 chữ số): 01 (Hà Nội), 02 (Hà Giang), ..., 99 (Cà Mau). Dùng để xác định tỉnh nơi đăng ký phương tiện.
2. **Chuỗi Chữ Cái** (1-2 ký tự): Ký tự từ A-Z, không sử dụng ký tự Việt (Ă, Â, Ê, Ô, Ơ, Ư). Dùng để phân loại phương tiện (VD: A cho ô tô 9 chỗ, B cho ô tô dưới 9 chỗ, C cho xe tải, v.v.). Một số chuỗi đặc biệt dùng cho nhà nước, quân sự.
3. **Chuỗi Chữ Số** (4-5 ký tự): Chữ số từ 0-9, dùng để đánh số thứ tự.

**Ví dụ:**
- "30-AB-12345" = Hà Nội (30), chuỗi AB, số 12345
- "01-A-1" = Hà Nội (01), loại A, số 1 (hiếm, biển VIP)
- "51-K-99999" = Đà Nẵng (51), loại K, số 99999

### 1.6.2. Loại Biển và Kích Thước

**Loại biển theo màu sắc** [12], [13]:

| Màu | Loại Phương Tiện | Ghi Chú |
|-----|------------------|---------|
| Trắng | Ô tô cá nhân | Chữ đen trên nền trắng |
| Vàng | Ô tô kinh doanh vận tải, dịch vụ | Chữ đen trên nền vàng |
| Xanh | Xe máy cá nhân | Chữ trắng trên nền xanh |
| Xanh đậm + Mã Tỉnh Trên | Phương tiện chính phủ, quân sự | Ít gặp |
| Đỏ | Đặc biệt (công an, quân đội) | Rất hiếm |

**Kích thước biển:**

- **Ô tô 2 biển:**
  - Biển ngắn (trước): 165 mm (cao) × 330 mm (rộng)
  - Biển dài (sau): 110 mm (cao) × 520 mm (rộng)
- **Xe máy 1 biển**: 110 mm (cao) × 200 mm (rộng)
- **Biển 2 hàng** (xe máy, tải nhỏ): 110 mm (cao) × 200 mm (rộng), hàng 1 = mã tỉnh + chữ cái, hàng 2 = chữ số.

Biển số là kim loại phản quang, được dập nổi các ký tự. Nền biển trắng/vàng/xanh, ký tự màu đen hoặc trắng tùy loại. Mặt phản quang giúp nhìn rõ vào buổi tối khi có đèn chiếu.

### 1.6.3. Font Chữ và Đặc Tính OCR

Ký tự trên biển số Việt Nam sử dụng font **Helvetica VN** hoặc **Font TT148** (do Bộ Công An định nghĩa), không phải font thường dùng trên máy tính. Đặc điểm:
- Ký tự có độ dày nhất định, không quá mảnh.
- Khoảng cách giữa các ký tự cố định, dễ dàng phân đoạn.
- Không có descender (phần nằm dưới baseline) nên dễ xác định vùng ký tự.

Từ góc độ OCR, những điểm lưu ý:
1. **Biển 2 hàng**: Phải xác định mấy hàng biển, sắp xếp đúng thứ tự ký tự (hàng 1 → hàng 2).
2. **Giãn cách**: Padding lề trên/dưới/trái/phải của biển không chuẩn có thể làm sai kết quả.
3. **Mài mòn**: Biển cũ, ký tự bị mài mòn, sẽ ảnh hưởng độ chính xác OCR.
4. **Góc chụp và ánh sáng**: Nếu góc lệch >15°, ký tự méo. Nếu ánh sáng quá sáng/tối, contrast sẽ xấu.

Một số nghiên cứu OCR cho biển Việt Nam đã thử nghiệm độ chính xác trên tập dữ liệu VNLP (Vietnam License Plate detection and recognition dataset), gồm hơn 37,000 ảnh. Kết quả: exact match ~37-55% tùy mô hình, character-level accuracy ~60-75%. Những con số này được coi là baseline, và cần fine-tuning hoặc post-processing để đạt >90% trong ứng dụng thực tế.

### 1.6.4. So Sánh với Biển Số Quốc Tế

[BẢNG 1.3: So sánh định dạng biển số giữa quốc gia]

| Đặc Tính | Việt Nam | EU | Hoa Kỳ | Trung Quốc |
|----------|---------|----|----|-----------|
| Mã Quốc Gia | Không | Có (trên trái) | Không | Không |
| Mã Tỉnh/Bang | 2 chữ số | 2 chữ cái | Thay đổi | 1 chữ cái |
| Format | Tỉnh-Chữ-Số | Chữ-Số-Chữ | Thay đổi | Chữ-Số-Chữ-Số |
| Số Ký Tự | 7-9 | 7-8 | 7 | 7-8 |
| Ký Tự | A-Z, 0-9 | A-Z, 0-9 | A-Z, 0-9 | Tiếng Trung, A-Z, 0-9 |
| Loại Phương Tiện | Màu biển | Prefix | Loại state | Màu nền |

Những khác biệt này có ý nghĩa với OCR: mô hình được huấn luyện trên biển Hoa Kỳ không thể áp dụng trực tiếp cho biển Việt Nam vì format khác, font khác, ký tự khác. Cần dataset và fine-tuning cụ thể cho từng quốc gia.

[HÌNH 1.5: Mẫu biển số Việt Nam (1 hàng) và (2 hàng) - So sánh kích thước, vị trí ký tự, vùng phản quang]

[HÌNH 1.6: So sánh biển số Việt Nam vs Hoa Kỳ vs EU - Khác biệt về layout, ký tự, màu sắc ảnh hưởng tới OCR]

---

## Tóm Tắt Chương

Chương 1 đã trình bày cơ sở lý thuyết cho hệ thống nhận diện biển số xe trong bối cảnh quản lý phương tiện tại cơ sở giáo dục. Các nội dung chính:

1. **Bài toán thực tế**: Quản lý thủ công hiện nay kém hiệu quả, cần tự động hóa. ANPR là công nghệ phù hợp, với thị trường toàn cầu phát triển nhanh 9%+ mỗi năm.

2. **ANPR gồm 4 giai đoạn**: Phát hiện phương tiện → Định vị biển → Phân đoạn ký tự → OCR. Công nghệ phát triển từ truyền thống sang deep learning sang end-to-end. Thách thức chính: ánh sáng, góc chụp, occlusion, motion blur, biển 2 hàng.

3. **YOLO (YOLOv8)**: Detector một giai đoạn cực nhanh, phù hợp real-time. YOLOv8n siêu nhẹ (3.2M param, 0.99ms), YOLOv8m chính xác cao (mAP 50%). Có thể dùng cho phát hiện phương tiện cũng như ký tự OCR.

4. **SORT**: Tracker đơn giản mà hiệu quả (260 Hz), dùng Kalman Filter + Hungarian Assignment. Không cần training, dễ triển khai. ID switch có thể cải tiến bằng ByteTrack nếu cần.

5. **Công nghệ web**: FastAPI (async backend), PostgreSQL (dữ liệu), React (dashboard), Docker (deployment). Kiến trúc hiện đại, mở rộng được.

6. **Biển số Việt Nam**: Format 2-tỉnh + 1-2-chữ + 4-5-số, đa loại màu, 1-2 hàng. Font Helvetica VN, kích thước chuẩn. Baseline OCR ~37-55% exact match, cần fine-tuning lên >90%.

Các lý thuyết trên là nền tảng kỹ thuật và tham khảo khoa học cho thiết kế chi tiết hệ thống, được trình bày ở các chương tiếp theo.

---

## Tài Liệu Tham Khảo

[1] Du, K., et al., "Automatic Number Plate Recognition (ANPR) in smart cities: A systematic review," *Comput. Environ. Urban Syst.*, vol. 96, p. 101847, 2022.

[2] "Automatic Number Plate Recognition: A Detailed Survey of Relevant Algorithms," *Sensors*, vol. 21, no. 9, art. 3028, May 2022.

[3] "A Survey of Automatic Number Plate Recognition and Parking Management System," in *Proc. Smart Energy Comput.*, Springer, 2024.

[4] "YOLOv8 vs. YOLOv5: A Comprehensive Technical Comparison," *Ultralytics YOLO Docs*, 2023.

[5] "Performance Comparison of YOLO Object Detection Models," *Learn OpenCV*, 2023.

[6] Zhu, Y., et al., "Performance Evaluation of YOLOv8 for Object Detection on the COCO Dataset," *Int. J. Res. Appl. Sci. Eng. Technol.*, vol. 12, 2024.

[7] "YOLOv5, YOLOv8 and YOLOv10: The Go-To Detectors for Real-time Vision," arXiv preprint arXiv:2407.02988, 2024.

[8] Bewley, A., Ge, Z., Ott, L., Ramos, F., and Upcroft, B., "Simple online and realtime tracking," in *2016 IEEE Int. Conf. Image Process. (ICIP)*, pp. 3464–3468, 2016.

[9] Bewley, A., et al., "Simple Online and Realtime Tracking," arXiv preprint arXiv:1602.00763, 2016.

[10] "ByteTrack: Multi-Object Tracking by Associating Every Detection Box," arXiv preprint, 2021.

[11] "Comparative Evaluation of SORT, DeepSORT, and ByteTrack for Multiple Object Tracking in Highway Videos," *Int. J. Sustain. Infrastruct. Cities Soc.*, 2024.

[12] "Circular 24/2023/TT-BCA: Procedures for issuance and revocation of vehicle registration and license plates," Ministry of Public Security, Vietnam, effective Aug. 15, 2023.

[13] "Vehicle registration plates of Vietnam," *Wikipedia*, updated 2024.

[14] "Regulations on license plates from 15/8/2023," *Vietnam.vn*, 2023.

[15] "FastAPI - Modern, fast (high-performance) web framework for building APIs with Python," https://fastapi.tiangolo.com/

[16] "PostgreSQL: The World's Most Advanced Open Source Relational Database," https://www.postgresql.org/

[17] "Build a back-end with PostgreSQL, FastAPI, and Docker," *Towards Data Science*, 2021.

[18] "Full stack, modern web application template using FastAPI, React, SQLModel, PostgreSQL, Docker," *GitHub tiangolo/full-stack-fastapi-postgresql*, https://github.com/tiangolo/full-stack-fastapi-postgresql

[19] "Docker to the Rescue: Deploying React And FastAPI App With Monitoring," *DEV Community*, 2023.

---

**Ghi Chú cho Tác Giả (User Edit)**

- [ ] Thêm các HÌNH 1.1 - 1.6 (sơ đồ, biểu đồ, ảnh biển số)
- [ ] Đọc qua, chỉnh sửa ngôn ngữ, thêm chi tiết nếu cần
- [ ] Xác nhận độ dài (nên ~12-15 pages), nếu quá dài có thể rút gọn 1.5, 1.6
- [ ] Kiểm tra trích dẫn [N] khớp với danh sách References
- [ ] Nếu cần thêm phần (ví dụ: 1.7 về Biên Pháp Xử Lý Dữ Liệu hay 1.8 về An Ninh), hãy thêm
