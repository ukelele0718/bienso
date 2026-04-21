# Chương 1: Cơ Sở Lý Thuyết

## 1.1. Đặt Vấn Đề và Tổng Quan Bài Toán

### 1.1.1. Bối Cảnh và Vấn Đề Thực Tế

Tại các cơ sở giáo dục đào tạo quy mô lớn như Đại học Bách khoa Hà Nội, quản lý phương tiện ra vào khuôn viên là một nhiệm vụ hành chính quan trọng. Hiện nay, hầu hết các trường đại học sử dụng phương pháp quản lý bán tự động: nhân viên bảo vệ ghi chép thủ công biển số xe khi xe vào/ra, sau đó đối soát với hồ sơ đăng ký. Mặc dù phương pháp này có thể chấp nhận được với lưu lượng xe vừa phải, nhưng nó phơi bày một loạt nhược điểm rõ rệt khi quy mô tăng.

Thứ nhất, trong giờ cao điểm khi lưu lượng xe tăng đột biến, nhân viên không thể ghi chép kịp tất cả các biển số. Sai sót xảy ra do nhân công: lẫn các ký tự tương tự (1-I, 0-O), bỏ sót những phương tiện, hoặc viết sai chữ. Thứ hai, việc tra cứu lịch sử vào/ra trở nên tốn thời gian, vì phải tìm kiếm thủ công trong các cuốn sổ hoặc file Excel không có cấu trúc, khó lập báo cáo thống kê. Thứ ba, hệ thống không thể phát hiện và cảnh báo tức thời khi phương tiện lạ hay bị cấm vào khuôn viên, vì quy trình kiểm tra được thực hiện sau một thời gian dài, không kịp can thiệp khi xe đang ở lối vào.

Nhu cầu tự động hóa quy trình này là rõ ràng. Một hệ thống tự động có thể: (1) nhận diện biển số xe trong thời gian thực từ video camera, (2) so khớp tức thời với cơ sở dữ liệu phương tiện được phép, (3) ghi nhận tự động lịch sử vào/ra với timestamp chính xác đến giây, (4) cảnh báo tức thời khi phát hiện bất thường như phương tiện không đăng ký hoặc có lệnh cấm. Đây chính là bài toán **Automatic Number Plate Recognition (ANPR)**, còn gọi là **License Plate Recognition (LPR)**, một công nghệ nhúng xử lý thời gian thực. 

ANPR không phải là một công cụ độc lập, mà là một hệ thống tích hợp gồm một loạt thành phần: camera đặc biệt, engine xử lý hình ảnh từ AI, backend cơ sở dữ liệu, và giao diện người dùng. Sự thành công của hệ thống ANPR phụ thuộc vào sự phối hợp chặt chẽ giữa tất cả các thành phần này, từ chất lượng ảnh input cho đến độ chính xác nhận dạng và tốc độ xử lý.

### 1.1.2. Mục Tiêu và Phạm Vi của Đồ Án

Mục tiêu chính của đồ án này là thiết kế và xây dựng một **prototype hệ thống quản lý phương tiện ra/vào** dựa trên công nghệ nhận diện biển số xe tự động. Hệ thống bao gồm ba thành phần chính có chức năng riêng biệt nhưng kết nối hữu cơ:

**Thứ nhất là AI Engine**, chịu trách nhiệm xử lý luồng video từ camera, phát hiện các phương tiện trong khung hình, định vị chính xác vùng biển số, và nhận dạng các ký tự trên biển để xuất ra chuỗi biển số hoàn chỉnh.

**Thứ hai là Backend**, tiếp nhận sự kiện nhận diện từ AI Engine (mỗi phương tiện được nhận diện là một sự kiện), xử lý logic kiểm soát rào chắn (barrier rules - quyết định xe có được vào/ra hay cần xác nhận), quản lý dữ liệu phương tiện, lưu trữ lịch sử toàn bộ các sự kiện vào cơ sở dữ liệu, xác thực quyền truy cập của các phương tiện được phép.

**Thứ ba là Dashboard**, giao diện web cho nhân viên bảo vệ và quản lý cơ sở, hiển thị các sự kiện nhận diện theo thời gian thực, cho phép tra cứu lịch sử, xem hình ảnh snapshot biển số để xác nhận thủ công khi cần thiết, và cung cấp thống kê lưu lượng xe theo thời gian.

Về phạm vi, đồ án tập trung vào **xây dựng prototype** với 1-2 camera đơn lẻ tại một cổng ra/vào, hỗ trợ cả xe máy và ô tô mà không phân biệt loại. Phạm vi **không bao gồm**: hệ thống phân tán với hàng chục camera (sẽ đòi hỏi kiến trúc RTSP streaming phức tạp, load balancing), nhận dạng ngoại hình người lái (face recognition), hoặc tích hợp đầy đủ với hệ thống quản lý bãi xe toàn diện. Thay vào đó, đồ án tập trung vào ba lĩnh vực ưu tiên: **(1) Độ chính xác OCR cao** trên biển số Việt Nam thông qua fine-tuning và post-processing, **(2) Xử lý theo thời gian thực** với tốc độ frame cao để không bỏ sót phương tiện, và **(3) Giao diện trực quan** dễ sử dụng cho người dùng cuối mà không đòi hỏi kỹ năng kỹ thuật.

### 1.1.3. Lợi Ích và Ứng Dụng

Triển khai hệ thống ANPR tại cơ sở giáo dục mang lại nhiều lợi ích đa chiều. **Đối với nhân viên bảo vệ**, công việc ghi chép thủ công được hoàn toàn loại bỏ, thời gian kiểm tra mỗi phương tiện rút ngắn từ vài phút xuống còn vài giây, và độ chính xác tăng vọt từ ~85% (thủ công) lên >95% (tự động). Khối lượng công việc lặp đi lặp lại được giảm thiểu, cho phép tập trung vào các nhiệm vụ an ninh quan trọng hơn.

**Đối với quản lý cơ sở**, hệ thống cung cấp thống kê chi tiết và thời gian thực: số lượng phương tiện vào/ra theo giờ/ngày, danh sách phương tiện bất thường hoặc không được phép, lịch sử di chuyển từng chiếc xe, hỗ trợ lập báo cáo an ninh toàn diện. Dữ liệu này giúp phát hiện các hành vi bất thường, quản lý dung lượng khuôn viên hiệu quả hơn, và cung cấp bằng chứng nếu cần xử lý sự cố.

**Về quy mô toàn cầu**, thị trường ANPR đang phát triển với tốc độ ấn tượng. Theo báo cáo thị trường của Fact MR năm 2024, thị trường ANPR toàn cầu có giá trị 4.14 tỷ USD năm 2025 và dự kiến đạt 9.27 tỷ USD vào năm 2034, với tốc độ tăng trưởng hàng năm (CAGR) là 9.36% [1]. Các ứng dụng chính bao gồm quản lý bãi xe thông minh (smart parking), trạm thu phí tự động (toll collection systems), hệ thống giao thông thông minh (Intelligent Transportation Systems - ITS), và giám sát bảo mật công khai. Các quốc gia phát triển như Hoa Kỳ, Anh, Nhật Bản đã triển khai ANPR rộng rãi tại các cổng vào thành phố, sân bay, và bãi xe công cộng. Ở Việt Nam, ANPR vẫn là lĩnh vực tương đối mới, với một số dự án thí điểm tại các cổng ra vào cơ sở công cộng lớn ở TP. Hồ Chí Minh và Hà Nội.

Hệ thống mà đồ án xây dựng sẽ góp phần chứng minh khả năng áp dụng ANPR vào bối cảnh giáo dục Việt Nam, cung cấp dữ liệu thực nghiệm và kinh nghiệm triển khai cho những dự án tương tự trong tương lai.

---

## 1.2. Tổng Quan về Công Nghệ Nhận Diện Biển Số Tự Động (ANPR/LPR)

### 1.2.1. Định Nghĩa và Cấu Trúc Hệ Thống

**Automatic Number Plate Recognition (ANPR)**, còn gọi là **License Plate Recognition (LPR)**, là một hệ thống nhúp xử lý thời gian thực, tự động phát hiện, trích xuất, và nhận dạng thông tin từ biển số phương tiện trong hình ảnh hoặc video [1]. Định nghĩa này tuy ngắn gọn nhưng ẩn chứa độ phức tạp lớn: ANPR không phải là một công cụ độc lập, mà là một **chuỗi các công đoạn xử lý hình ảnh kết hợp với nhận dạng ký tự**, mỗi công đoạn có mục tiêu và thách thức riêng.

Một hệ thống ANPR điển hình bao gồm bốn giai đoạn liên tiếp [2]:

**Giai đoạn 1: Phát Hiện Phương Tiện (Vehicle Detection)** — Từ một frame hình ảnh đầu vào (do camera cung cấp hoặc trích từ video), mô hình học sâu (thường là YOLO, Faster R-CNN) phát hiện vị trí tất cả các phương tiện (ô tô, xe máy, xe tải) có mặt trong khung hình. Đầu ra của giai đoạn này là danh sách các bounding box — các hình chữ nhật bao quanh mỗi xe — với tọa độ (x, y, chiều rộng, chiều cao) và độ tin cậy (confidence score).

**Giai đoạn 2: Định Vị Vùng Biển Số (Plate Localization)** — Trong mỗi vùng phương tiện được phát hiện từ bước 1, hệ thống xác định vị trí chính xác của biển số. Các phương pháp khác nhau có thể áp dụng: mô hình YOLO riêng biệt được huấn luyện cụ thể cho biển số, hoặc heuristic dựa trên đặc tính hình ảnh như vùng phản quang, màu sắc, hoặc kết cấu đặc trưng của biển kim loại. Mục tiêu là tách riêng vùng biển ra khỏi phần còn lại của xe.

**Giai đoạn 3: Phân Đoạn Ký Tự (Character Segmentation)** — Vùng biển được chia thành các vùng con, mỗi vùng tương ứng với một ký tự (chữ cái hoặc chữ số). Bước này là quan trọng nhưng đầy thách thức: biển số 2 hàng (phổ biến ở xe máy Việt Nam) có thể gây nhầm lẫn, biển bẩn hoặc bị che khuất một phần sẽ làm khó khăn sự phân chia chính xác.

**Giai đoạn 4: Nhận Dạng Ký Tự (OCR)** — Mỗi ký tự đã được tách riêng được đưa vào mô hình nhận dạng ký tự (OCR - Optical Character Recognition). Mô hình này có thể dùng CNN + CTC (Connectionist Temporal Classification), CRNN (Convolutional Recurrent Neural Network), hoặc LPRNet, để xác định giá trị của từng ký tự. Kết quả cuối cùng là chuỗi ký tự đầy đủ, ví dụ "30-AB-12345".

Hiệp thương tế giữa các giai đoạn này là rất quan trọng: **lỗi ở bước detection sẽ dẫn tới bỏ sót các biển số** (một số sẽ không được xử lý tiếp), **lỗi ở localization sẽ cắt biển không đúng** (ký tự ở mép bị mất), và **lỗi ở OCR sẽ cho kết quả nhầm lẫn ký tự** (một chữ "1" bị nhận thành "l" hoặc "I"). Do đó, cải tiến từng giai đoạn là cần thiết để tăng độ chính xác tổng thể của hệ thống.

### 1.2.2. Tiến Hóa Công Nghệ ANPR

Nghiên cứu và triển khai ANPR đã phát triển qua ba thế hệ công nghệ chính [1], mỗi giai đoạn mang lại những cải tiến về độ chính xác hoặc tốc độ.

**Thế hệ 1: Xử Lý Hình Ảnh Truyền Thống (2000-2010).** Phương pháp này dựa hoàn toàn trên các kỹ thuật xử lý hình ảnh cơ bản: phát hiện cạnh (edge detection), phân tích kết cấu (texture analysis), phân ngưỡng (thresholding) để tách vùng màu biển khỏi background. Ưu điểm là tốc độ xử lý rất nhanh (có thể chạy trên hardware yếu) và không đòi hỏi tập dữ liệu huấn luyện lớn. Tuy nhiên, phương pháp này rất kém bền vững trước các biến động của điều kiện thực tế: ánh sáng thay đổi, góc chụp không chuẩn, hoặc biển bẩn/cũ sẽ làm giảm đáng kể độ chính xác. Nhận dạng ký tự dựa trên template matching (so sánh mẫu) hoặc máy học cổ điển (Support Vector Machine - SVM) cũng có độ chính xác thấp, khoảng 60-70% trên dữ liệu thực.

**Thế hệ 2: Học Sâu Đa Giai Đoạn (2015-2020).** Sự xuất hiện của deep learning (Convolutional Neural Networks - CNN, Recurrent Neural Networks - RNN) cho phép xây dựng các mô hình riêng cho mỗi giai đoạn ANPR, được huấn luyện trên tập dữ liệu lớn. Ví dụ điển hình: Faster R-CNN cho vehicle detection, mô hình YOLO hoặc SSD cho plate localization, CRNN + CTC cho OCR ký tự. Mỗi mô hình được tối ưu hóa riêng biệt, cho độ chính xác cao hơn đáng kể (khoảng 85-90% exact match trên biển quốc tế). Tuy nhiên, phương pháp này yêu cầu huấn luyện và điều chỉnh nhiều mô hình khác nhau, tốc độ xử lý tổng hợp có thể chậm hơn do phải chạy tuần tự qua bốn giai đoạn.

**Thế hệ 3: End-to-End Neural Networks (2020-nay).** Các mô hình mới cố gắng học toàn bộ quy trình từ ảnh thô đến kết quả biển số trong một mô hình duy nhất, hoặc giảm số lượng mô hình xuống 2-3 thành phần chính. Lợi ích của cách tiếp cận này là tối ưu hóa toàn cục (global optimization), giảm độ trễ tích lũy từ việc chuyển dữ liệu giữa các mô hình, và dễ triển khai (chỉ cần load một hoặc hai mô hình). Các công bố gần đây tập trung vào việc cải tiến end-to-end recognition models, tăng tốc độ xử lý, và cải thiện khả năng generalization trên dữ liệu từ các miền (domain) khác nhau.

### 1.2.3. Thách Thức Chính của ANPR

Dù công nghệ đã tiến bộ nhiều so với những năm 2000, ANPR vẫn gặp phải một loạt thách thức thực tế trong triển khai [2]:

**Điều Kiện Ánh Sáng Thay Đổi (Lighting Variations).** Ảnh chụp vào buổi sáng với ánh sáng mặt trời mạnh, buổi tối với ánh đèn tích lũy, hoặc trời mây che phủ, đều tạo ra ảnh hưởng đáng kể tới chất lượng hình ảnh. Độ tương phản của biển số, độ phản quang, và kênh màu sắc đều thay đổi, làm khó cho các mô hình detection và OCR được huấn luyện trên dữ liệu có điều kiện ánh sáng chuẩn.

**Góc Chụp Không Ổn Định (Viewing Angles).** Nếu camera không đặt vuông góc với xe hoặc phương tiện đi lệch so với camera, biển sẽ bị méo theo phối cảnh (perspective distortion), ký tự bị nén hoặc giãn, gây khó khăn cho OCR. Góc lệch lớn hơn 30° có thể làm sai lệch kết quả nhận dạng một cách đáng kể.

**Vật Cản Che Khuất (Occlusion).** Phần biển bị che bởi xe khác, bụi bẩn, bùn, hoặc bị hư hỏng, dẫn tới mất mát thông tin của các ký tự, làm giảm độ tin cậy của OCR hoặc thậm chí không nhận dạng được biển.

**Mờ Chuyển Động (Motion Blur).** Khi xe di chuyển nhanh khi quay frame hoặc camera bị rung, biển sẽ bị mờ, ký tự không rõ ràng, độ chính xác OCR giảm mạnh.

**Biển Số Nhiều Hàng (Multi-row Plates).** Một số phương tiện như xe máy, xe tải nhỏ sử dụng biển 2 hàng, trong đó mã tỉnh + chữ cái ở hàng trên, chữ số ở hàng dưới. Việc phân đoạn và sắp xếp lại ký tự theo đúng thứ tự, nhất là khi có khoảng cách lớn giữa hai hàng, là phức tạp.

Để đối mặt với những thách thức này, các hệ thống commercial cao cấp (ví dụ: sản phẩm của Hikvision, Dahua) đã tối ưu hóa thông qua tiền xử lý hình ảnh (pre-processing), tăng cường dữ liệu (augmentation), sử dụng nhiều mô hình tương tự (ensemble models), và tuning chuyên sâu. Tuy nhiên, mỗi khu vực địa lý (quốc gia, thậm chí tỉnh) có những đặc tính khác nhau về format biển, loại phương tiện, và điều kiện ghi, nên mô hình cần được fine-tune cụ thể cho từng khu vực để đạt hiệu suất tối ưu.

---

## 1.3. Công Nghệ YOLO: Phát Hiện Đối Tượng Theo Thời Gian Thực

### 1.3.1. Kiến Trúc và Nguyên Lý YOLO

**YOLO (You Only Look Once)** là một họ mô hình phát hiện đối tượng (object detection) độc lập, được Redmon et al. giới thiệu năm 2016 [4], [5]. Khác với các phương pháp hai giai đoạn (two-stage detectors) như Faster R-CNN, YOLO là một detector **một giai đoạn (single-shot detector)**: nó chia hình ảnh thành một lưới các ô (grid), và từ mỗi ô lưới, dự đoán trực tiếp bounding box của vật thể và lớp (class) của nó. Ưu điểm chính là tốc độ xử lý vô cùng nhanh, phù hợp cho ứng dụng real-time nơi latency là yếu tố quan trọng.

**Nguyên lý hoạt động:** Đầu vào là ảnh có kích thước chuẩn (416×416 hoặc 640×640 tùy phiên bản). Một **backbone CNN** (mạng nơ-ron tích chập chính) trích xuất các đặc trưng (features) từ ảnh gốc, giảm kích thước nhưng tăng tính chất ngữ nghĩa. Các đặc trưng này được đưa vào **cổ cây (neck)** — một chuỗi các lớp kết hợp và nâng cấp, thường sử dụng Feature Pyramid Network (FPN) để xử lý đa tỷ lệ, giúp phát hiện được vật thể nhỏ lẫn vật thể lớn. Cuối cùng, **head (đầu)** của mạng dự đoán ba thứ: (1) điểm tin cậy (objectness score) cho mỗi ô lưới, (2) bounding box (x, y, width, height) tương đối với ô lưới, (3) xác suất class cho mỗi lớp đối tượng (vehicle, person, etc.).

**Lịch sử phát triển YOLO** giới thiệu một loạt cải tiến cấu trúc và training:

- **YOLOv1 (2016)**: Mô hình gốc được giới thiệu, phát hiện lên đến 98 lớp đối tượng, độc lập với Faster R-CNN.
- **YOLOv3 (2018)**: Cải tiến backbone (Darknet-53 thay vì Darknet-19), dự đoán đa tỷ lệ (multi-scale predictions), huấn luyện trên 80 lớp COCO.
- **YOLOv4 (2020)**: Giới thiệu các cải tiến training như Data Augmentation mạnh mẽ, Bag of Freebies (kỹ thuật tăng chất lượng không tốn chi phí tính toán), Bag of Specials (tối ưu hóa kiến trúc).
- **YOLOv5 (2020)**: Tối ưu hóa mã nguồn, tăng tốc độ, vẫn sử dụng anchor boxes.
- **YOLOv8 (2023)**: Loại bỏ hoàn toàn cơ chế anchor boxes, sử dụng anchor-free head, tăng độ chính xác, tốc độ nhanh hơn [4].

### 1.3.2. YOLOv8 Nano: Phiên Bản Siêu Nhẹ

Để phục vụ ứng dụng edge deployment (triển khai tại thiết bị có tài nguyên hạn chế như camera IP thông minh, Jetson Nano), công ty Ultralytics phát hành các phiên bản **lightweight** (nhẹ) của YOLOv8. **YOLOv8 Nano (YOLOv8n)** là phiên bản nhỏ nhất trong dòng sản phẩm [4], [6]:

- **Số tham số mô hình**: 3.2 triệu (so với 11.2 triệu của YOLOv8s, 68 triệu của YOLOv8m), cho phép chạy trên device có bộ nhớ hạn chế.
- **GFLOPs**: 8.7 (ở đầu vào 640×640), tức là chỉ cần khoảng 1/100 lượng tính toán so với mô hình lớn, giúp tiết kiệm năng lượng và giảm latency.
- **mAP trên COCO**: 37.3% (thấp hơn YOLOv8s 44.9%, nhưng vẫn chấp nhận được cho ứng dụng real-time nơi tốc độ được ưu tiên).
- **Tốc độ**: 0.99 millisecond trên GPU A100 với TensorRT optimization, có khả năng chạy ở 100+ FPS (frames per second).
- **Kiến trúc**: CSP backbone (Darknet cơ bản với Cross Stage Partial connection), PAN-FPN neck, anchor-free head. So với YOLOv8s, độ sâu mạng (depth) bị giảm 33% và chiều rộng (width) giảm 25%.

**YOLOv8n rất phù hợp** cho ứng dụng phát hiện phương tiện tại cơ sở giáo dục, vì: (1) vùng giám sát được giới hạn (chỉ một cổng vào/ra), (2) lưu lượng xe không cao như cổng quốc lộ, (3) chủ yếu cần tốc độ xử lý cao và độ chính xác khá (không cần siêu cao). Thêm vào đó, YOLOv8n có thể chạy được trên GPU cấp entry-level (GTX 1050, RTX 3050) hoặc thậm chí CPU nếu chấp nhận latency cao hơn.

### 1.3.3. Ứng Dụng YOLO cho Phát Hiện Ký Tự trong OCR

Ngoài phát hiện phương tiện, YOLO còn có thể được sử dụng để phát hiện **từng ký tự riêng lẻ** trên biển số [4], [7]. Phương pháp này khác với segmentation (phân tách): thay vì phân tách ảnh thành các vùng đơn sắc dựa trên ngưỡng, ta huấn luyện một mô hình YOLO để nhận ra 36 lớp (26 chữ cái A-Z + 10 chữ số 0-9), và mô hình sẽ phát hiện bounding box của mỗi ký tự riêng biệt.

**Lợi ích** của cách tiếp cận này: (1) không cần bước phân đoạn thủ công dựa trên ngưỡng, (2) có thể xử lý biển bẩn, méo, hoặc chuyển động, vì YOLO bền vững hơn template matching, (3) kết hợp với OCR truyền thống hoặc OCR dựa trên CNN, mô hình có thể đạt độ chính xác cao. **Nhược điểm:** cần tập dữ liệu lớn với annotation ký tự riêng lẻ (labeling thủ công rất tốn kém), và cần computational resources để huấn luyện.

### 1.3.4. So Sánh YOLO với Các Detector Khác

Để đặt YOLO vào bối cảnh các detector khác, bảng dưới so sánh các mô hình phát hiện đối tượng chính:

| Mô hình | Kiểu | mAP COCO | Tốc độ (ms/640) | Tham số | Ứng dụng |
|--------|------|----------|-----------|--------|---------|
| Faster R-CNN | Two-stage | 42.7% | 140 | 41.8M | Chính xác cao, tốc độ thấp |
| SSD300 | One-stage | 41.4% | 20 | 26.3M | Cân bằng chính xác-tốc độ |
| YOLOv5s | One-stage | 43.0% | 3.2 | 7.2M | Real-time, production-ready |
| YOLOv8n | One-stage | 37.3% | 0.99 | 3.2M | Ultra-lightweight, edge |
| YOLOv8m | One-stage | 50.2% | 3.8 | 25.9M | Chính xác cao + nhanh |

**Nhận xét:** YOLOv8n là lựa chọn tối ưu cho **edge deployment** (tốc độ so với tham số tối thiểu), trong khi YOLOv8m phù hợp cho **backend server** nếu có tài nguyên (mAP cao). Ứng dụng ANPR tại cơ sở giáo dục, nếu có GPU server mạnh, có thể sử dụng YOLOv8m để tăng độ chính xác phát hiện phương tiện dưới các điều kiện khó khăn (đêm khuya, trời mưa).

---

## 1.4. Theo Dõi Đa Đối Tượng Theo Thời Gian Thực với SORT

### 1.4.1. Bài Toán Theo Dõi Đa Đối Tượng (Multi-Object Tracking)

Khi xử lý video từ camera, mỗi frame (khung hình) được xử lý độc lập bởi bước detection phía trước (YOLO). Tuy nhiên, để quản lý từng phương tiện, cần biết **danh tính của nó qua các frame liên tiếp** — đây là bài toán **Multi-Object Tracking (MOT)**. Ví dụ cụ thể: nếu một xe máy vào khung hình từ trái sang phải, bước detection sẽ phát hiện nó ở frame 10, frame 11, frame 12, v.v., nhưng **cần ghi nhận rằng "xe ID=5 ở frame 10" và "xe ID=5 ở frame 11" là cùng một chiếc xe**, không phải hai xe khác nhau. Nếu không có tracking, mỗi frame sẽ được xem là phương tiện độc lập, dẫn tới ghi nhận sự kiện "phương tiện vào" 10 lần thay vì 1 lần.

**Bài toán MOT** bao gồm ba thành phần chính: 

**(1) Detection**: Phát hiện vị trí vật thể ở mỗi frame (đã giải quyết bởi YOLOv8 từ phần 1.3). 

**(2) Association (Phối hợp)**: Quyết định detection nào ở frame t ứng với track nào từ frame t-1. Đây là phần khó nhất, vì phải giải quyết các tình huống như vật thể biến mất tạm thời, hai vật thể xuyên qua nhau, hoặc phát hiện giả (false positive). 

**(3) State Management**: Cập nhật vị trí, vận tốc, và trạng thái (active, occluded, terminated) của mỗi track theo thời gian.

**Giải pháp hiệu quả nhất** dựa trên kết hợp **Kalman Filter** (dự báo vị trí tiếp theo dựa trên vận tốc) với **Hungarian Algorithm** (tối ưu hóa phép gán detection-to-track). Đây chính là nguyên lý của thuật toán SORT, được giới thiệu dưới đây.

### 1.4.2. SORT: Mô Hình Kalman và Hungarian Assignment

**SORT (Simple Online and Realtime Tracking)** được Bewley et al. giới thiệu năm 2016 tại IEEE ICIP [8], [9]. Thuật toán này nổi bật vì tính thanh lịch: đạt tốc độ cực nhanh (260 Hz) mà chỉ dùng các kỹ thuật cổ điển, không cần huấn luyện mạng nơ-ron.

**Bước 1: Biểu Diễn Trạng Thái (State Representation).** Mỗi vật thể theo dõi được biểu diễn bằng một **vector trạng thái 7 chiều**:
- (x, y) = tọa độ tâm của bounding box
- s = diện tích (scale) của bounding box
- r = tỉ lệ chiều rộng/chiều cao (aspect ratio)
- (vx, vy, vs) = vận tốc tương ứng của các thành phần trên

**Mô hình động** được giả định là **constant velocity model**: vị trí mới tại frame t = vị trí tại frame t-1 + vận tốc × Δt (thời gian giữa hai frame). Giả định này là hợp lý cho các vật thể chuyển động với vận tốc gần như hằng số trong khoảng thời gian ngắn (một vài frame).

**Bước 2: Dự Báo (Prediction)** sử dụng **Kalman Filter**. Từ trạng thái ở frame t-1, Kalman Filter dự báo (predict) trạng thái ở frame t. Kalman Filter bao gồm hai pha:
- **Predict phase**: Tính toán ước lượng tiên nghiệm (prior estimate) và ma trận hiệp phương sai lỗi dự báo dựa trên mô hình động.
- **Update phase**: Khi mới có phép đo (detection) từ frame t, cập nhật ước lượng hậu nghiệm (posterior estimate) bằng cách cân bằng giữa dự báo (đã tính ở pha predict) và phép đo mới. Cân bằng này được tối ưu hóa theo nguyên lý bình phương tối thiểu (least squares), giả định tiếng ồn là Gaussian.

**Tính chất quan trọng** của Kalman Filter: nó cho phép hệ thống **khoan dung với thiếu detection** (nếu frame t không phát hiện vật thể, track vẫn được duy trì bằng dự báo thay vì bị xóa ngay), và **tự động bỏ qua detection sai lệch** (outliers) nếu chúng quá xa khỏi dự báo.

**Bước 3: Phối Hợp (Association).** Sau khi dự báo, cần gán các detection từ frame t với các tracks dự báo từ frame t-1. Quá trình này gồm các bước:

1. Tính **ma trận Intersection-over-Union (IoU)** giữa mỗi detection và mỗi predicted bounding box. IoU = (diện tích giao) / (diện tích hợp), giá trị từ 0 (không trùng) đến 1 (trùng hoàn toàn).

2. Chuyển đổi IoU thành **ma trận chi phí (cost matrix)** với công thức: chi phí = 1 - IoU.

3. Giải bài toán **optimal assignment** bằng **Hungarian Algorithm**, một thuật toán cổ điển từ lĩnh vực combinatorial optimization. Thuật toán này tìm phép gán một-một (one-to-one matching) giữa detection và track sao cho **tổng chi phí là tối thiểu**, độ phức tạp là O(n³).

4. **Cập nhật tracks**: Các detection được gán (cost nhỏ hơn ngưỡng, thường 0.7) được đưa vào cập nhật Kalman Filter của track tương ứng. Detection không được gán sẽ tạo track mới. Track không được gán là "missing" — nếu không được gắn lại trong vài frame liên tiếp (thường 30 frame), sẽ bị loại bỏ.

### 1.4.3. Hiệu Suất và So Sánh với Các Tracker Khác

SORT có những đặc điểm nổi bật [8], [9], [11]:

**Tốc độ Cực Nhanh**: SORT đạt **260 Hz** (từ một video 60 fps, có thể xử lý 4 frame cùng lúc), nhanh hơn **20 lần** so với các tracker khác thời kỳ 2016. Điều này có thể do SORT chỉ dùng các phép toán hình học đơn giản, không liên quan tới neural network.

**Tính Đơn Giản**: Không cần CNN backbone hoặc trích xuất deep appearance feature, chỉ dùng hình học (IoU) và Kalman Filter. Code Python tinh gọn (dưới 1000 dòng), dễ hiểu, dễ sửa, dễ tùy chỉnh cho các bài toán cụ thể.

**Không Cần Training**: Kalman Filter là phương pháp thống kê, không cần huấn luyện trên dữ liệu, chỉ cần thiết lập các thông số hiệp phương sai (covariance matrices) một cách hợp lý.

**Tuy nhiên, SORT cũng có nhược điểm:** **ID Switch** — khi hai vật thể xuyên qua nhau hoặc quay lại cùng khu vực, IoU có thể làm nhầm lẫn danh tính. Các phương pháp **nâng cao** như:

- **DeepSORT** (2017) [9] giải quyết ID switch bằng cách thêm **deep appearance feature** — một embedding vector 128 chiều mô tả hình dáng/màu sắc của vật thể. Trong phối hợp, thay vì chỉ dùng IoU, ta cân nhân thêm khoảng cách cosine giữa các feature vectors. Tuy nhiên, DeepSORT chậm hơn (30-40 Hz) do cần chạy CNN.

- **ByteTrack** (2021) [10] đề xuất chiến lược phối hợp **hai giai đoạn**: trước tiên gắn tất cả các detection có confidence cao, sau đó recover detection confidence thấp bằng cách kiểm tra xem nó có gần track nào không. Cách này giảm ID switch mà vẫn giữ tốc độ cao (>100 Hz), đạt MOTA 77.3% trên tập benchmark MOT17.

**Lựa chọn cho ứng dụng ANPR:** SORT là lựa chọn lý tưởng cho quản lý phương tiện tại cơ sở giáo dục, vì: 

(1) Lưu lượng xe không quá dày đặc (không có nhiều xuyên qua so với giải đua xe), (2) Tốc độ xử lý yêu cầu <100 FPS (SORT đạt 260 Hz), (3) Triển khai đơn giản (code ngắn, không cần GPU mạnh), (4) Nếu cần cải tiến sau này, có thể nâng cấp lên ByteTrack mà không thay đổi toàn bộ kiến trúc.

**Bảng So Sánh Trackers:**

| Tracker | Giai đoạn | Độ Phức Tạp | Tốc độ (Hz) | MOTA | ID Switch | Ứng dụng |
|---------|-----------|-----------|----------|------|-----------|---------|
| SORT | Kalman + Hungarian | O(n³) | 260 | - | Cao | Real-time, mật độ thấp |
| DeepSORT | + CNN Feature | O(n²×m) | 30-40 | - | Thấp | Chính xác cao, tốc độ thứ cấp |
| ByteTrack | Two-stage matching | O(n×m) | >100 | 77.3% | Trung bình | Cân bằng tốt |

---

## 1.5. Công Nghệ Web cho Hệ Thống Giám Sát Khuôn Viên

### 1.5.1. Backend Web: FastAPI

Để tiếp nhận sự kiện nhận diện từ AI Engine (mỗi phương tiện được nhận diện là một sự kiện trong vòng vài mili giây), xử lý logic (kiểm tra quy tắc rào chắn, cập nhật cơ sở dữ liệu), và cung cấp API cho dashboard, cần một framework web **hiệu suất cao** và **đáng tin cậy**. **FastAPI** [15] là lựa chọn tối ưu cho ứng dụng này.

**FastAPI** là một framework web hiện đại cho Python, ra mắt năm 2018 bởi Sebastián Ramírez. Những ưu điểm chính:

**Hiệu Suất Async**: Sử dụng `async/await` của Python, FastAPI cho phép xử lý hàng trăm request đồng thời mà không cần threading hoặc multiprocessing phức tạp. Điều này rất quan trọng khi AI Engine gửi event liên tục mà cần độ lặng hồi (latency) thấp.

**Validation Tự Động bằng Pydantic**: Khi một request gửi đến, FastAPI tự động kiểm tra dữ liệu khớp với schema được định nghĩa trước. Nếu sai, trả về lỗi HTTP 422 (Unprocessable Entity) với chi tiết, giúp AI Engine biết phải gửi dữ liệu đúng format.

**OpenAPI/Swagger Docs Tự Động**: Từ code Python, FastAPI tự sinh file `openapi.json` và giao diện Swagger UI tương tác, rất tiện lợi cho developer khi debug hoặc test API.

**Tích Hợp SQLAlchemy ORM**: Kết nối Database được quản lý dễ dàng, session và transaction được xử lý sạch sẽ, giảm bug liên quan tới database.

**Vai trò trong hệ thống:**

1. Tiếp nhận POST request từ AI Engine, chứa thông tin biển số nhận diện, timestamp, confidence score.
2. Thực hiện logic **barrier rule** (quy tắc rào chắn): check biển số có trong danh sách phương tiện được phép không, nếu không tạo account tạm thời với số dư ban đầu.
3. Lưu event vào cơ sở dữ liệu (log timestamp, confidence, hình ảnh snapshot).
4. Broadcast event tới dashboard qua **WebSocket** (kết nối hai chiều) để push sự kiện real-time thay vì dashboard phải poll liên tục.
5. Cung cấp REST API cho dashboard để tra cứu sự kiện, tài khoản, phương tiện theo nhiều tiêu chí khác nhau.

**Hiệu suất kỳ vọng**: Mỗi request nhận diện từ AI Engine mất khoảng 50-100ms xử lý (bao gồm logic, database insert, validation), có thể xử lý 10-20 request/giây, tương ứng 10-20 phương tiện/giây qua cổng, nằm trong dự tính cho cơ sở giáo dục.

### 1.5.2. Cơ Sở Dữ Liệu: PostgreSQL

Để lưu trữ dữ liệu dài hạn và hỗ trợ tra cứu phức tạp (ví dụ: tìm tất cả sự kiện của biển số XYZ trong tuần qua), sử dụng **PostgreSQL** [16] — một cơ sở dữ liệu quan hệ nguồn mở mạnh mẽ nhất hiện nay.

**Schema dữ liệu cơ bản** của hệ thống bao gồm:

| Bảng | Mục Đích | Chi Tiết |
|------|---------|---------|
| `vehicles` | Danh sách phương tiện đăng ký | id, plate_number, owner, vehicle_type, status |
| `events` | Lịch sử sự kiện vào/ra | id, vehicle_id, timestamp, confidence, gate_type (IN/OUT) |
| `license_plate_reads` | Kết quả OCR chi tiết | id, event_id, plate_text, char_scores (mảng) |
| `cameras` | Thông tin camera | id, location, direction, ip_address, status |
| `users` | Tài khoản nhân viên bảo vệ/quản lý | id, name, role, password_hash |
| `accounts` | Tài khoản phương tiện tạm | id, plate_number, balance, created_at, expires_at |

**PostgreSQL có nhiều ưu điểm:**

**ACID Compliance**: Đảm bảo tính toàn vẹn dữ liệu thông qua Atomicity (mọi operation hoặc toàn bộ hoặc không), Consistency (trạng thái hợp lệ), Isolation (transaction không xung đột), Durability (dữ liệu được lưu vĩnh viễn). Ngay cả khi server bị dừng đột ngột, dữ liệu không bị mất hoặc hỏng.

**JSON Support**: PostgreSQL có loại dữ liệu JSON native, cho phép lưu mảng độ tin cậy từng ký tự OCR dưới dạng JSON, dễ query và không cần table con.

**Indexes**: Tạo B-tree index trên các cột thường xuyên query (`plate_number`, `timestamp`) để tra cứu nhanh O(log n) thay vì O(n).

**Scalability**: Hỗ trợ table partitioning (chia nhỏ bảng lớn) theo tháng hoặc quý, replication cho high availability, connection pooling.

**Ứng dụng tại cơ sở giáo dục:** PostgreSQL được chạy trong một container Docker, tách biệt khỏi FastAPI backend. Dữ liệu được backup định kỳ (hàng ngày), cho phép phục hồi trong trường hợp thảm họa.

### 1.5.3. Frontend Web: React + TypeScript

**Dashboard** của hệ thống là giao diện web cho nhân viên bảo vệ và quản lý. Sử dụng **React** [19] kết hợp **TypeScript** để đảm bảo **type-safety** — biên dịch sẽ bắt lỗi kiểu dữ liệu tại dev time thay vì runtime.

**Các thành phần chính của dashboard:**

**1. Live Counter**: Hiển thị số phương tiện vào/ra trong hôm nay (hoặc tuần/tháng), cập nhật real-time qua WebSocket mỗi khi có sự kiện mới.

**2. Recent Events Table**: Bảng danh sách các sự kiện mới nhất (20-50 sự kiện gần nhất), hiển thị biển số, thời gian, gate (vào/ra), confidence score, trạng thái xác nhận (confirmed/pending/rejected).

**3. Verify Queue**: Hàng đợi những sự kiện cần xác nhận thủ công — ví dụ biển số không rõ (confidence < 80%), hoặc không nằm trong danh sách đăng ký. Nhân viên có thể click để xem ảnh snapshot biển số (từ camera), confirm (xác nhận biển số đúng) hoặc reject (loại bỏ, phân loại là false positive).

**4. Search & Filter**: Tra cứu sự kiện theo nhiều tiêu chí: ngày (date picker), biển số (text search), gate (dropdown), trạng thái (confirmed/pending), cho phép xuất kết quả ra CSV để lập báo cáo.

**5. Statistics Chart**: Biểu đồ lưu lượng xe theo giờ (bar chart hoặc line chart), so sánh vào vs ra, hoặc thống kê theo loại phương tiện (xe máy vs ô tô).

**React được chọn vì:**

**Component-Based Architecture**: Mỗi thành phần (counter, table, chart) là một component độc lập, có thể tái sử dụng ở nhiều nơi, dễ bảo trì.

**TypeScript Type Safety**: Bắt lỗi type tại compile time, giảm đáng kể bug runtime.

**Rich Ecosystem**: Thư viện cho biểu đồ (Recharts, Chart.js), bảng dữ liệu (TanStack Table, AG Grid), form validation, HTTP client (Axios) rất phong phú.

**Real-time Support**: WebSocket library (socket.io, ws) tích hợp dễ dàng để nhận real-time event từ backend.

### 1.5.4. Containerization: Docker

Để dễ triển khai, mở rộng, và tái sản xuất môi trường, toàn bộ hệ thống được đóng gói thành **Docker containers** [19]:

```
docker-compose.yml:
  - ai-engine: Service xử lý video (tùy chọn, có thể chạy riêng trên GPU machine)
  - fastapi-backend: Container chứa FastAPI app + Python dependencies
  - postgresql-db: Container chứa PostgreSQL database
  - react-dashboard: Container chứa React app được build static, serve bằng Nginx
```

**Lợi ích:**

**Isolation**: Mỗi service (backend, database, frontend) có môi trường riêng, dependencies riêng, không xung đột hoặc ảnh hưởng lẫn nhau.

**Portability**: Chạy trên laptop dev (Windows/Mac), server production (Linux), hoặc cloud platform (AWS, Azure) mà không cần thay đổi code.

**Scaling**: Dễ dàng spin up nhiều backend instances, load balance bằng reverse proxy (Nginx), auto-restart nếu crash.

**Version Control**: Image Docker có tag version, dễ rollback nếu phiên bản mới có bug.

---

## 1.6. Đặc Tính Biển Số Xe Việt Nam

### 1.6.1. Khung Pháp Lý và Định Dạng

Theo **Thông Tư 24/2023/TT-BCA** (hiệu lực từ 15 tháng 8 năm 2023) của Bộ Công An Việt Nam [12], biển số xe Việt Nam phải tuân theo các chuẩn mới. Thông Tư này thay thế Thông Tư 58/2020/TT-BGTVT, chủ yếu bổ sung quy định về quản lý kỹ thuật an ninh, tính xác thực của biển, và quy trình cấp phát. Những thay đổi này nhằm tăng độ bảo mật, ngăn chặn biển số giả mạo, và hiện đại hóa quản lý phương tiện.

**Định dạng biển số Việt Nam** bao gồm ba thành phần rõ ràng:

**1. Mã Tỉnh** (2 chữ số): Từ 01 (Hà Nội) đến 99 (Cà Mau), xác định tỉnh nơi đăng ký phương tiện. Dùng để quản lý thống kê địa phương.

**2. Chuỗi Chữ Cái** (1-2 ký tự): Ký tự từ A-Z, không sử dụng ký tự Việt (Ă, Â, Ê, Ô, Ơ, Ư) để tránh nhầm lẫn với quốc tế. Dùng để phân loại phương tiện: ví dụ A cho ô tô 9 chỗ, B cho ô tô dưới 9 chỗ, C cho xe tải, K cho xe khách, v.v. Một số chuỗi đặc biệt dành cho nhà nước, quân sự (thường bắt đầu bằng QH, QS).

**3. Chuỗi Chữ Số** (4-5 ký tự): Chữ số từ 0-9, dùng để đánh số thứ tự cấp phát. Chuỗi dài 4-5 số cho phép khoảng 90,000-900,000 biển cho mỗi tỉnh và loại, đủ cho nhu cầu.

**Ví dụ cụ thể:**
- "30-AB-12345" = Hà Nội (30), chuỗi AB, số 12345
- "01-A-1" = Hà Nội (01), loại A, số 1 (hiếm, biển VIP)
- "51-K-99999" = Đà Nẵng (51), loại K (xe khách), số 99999

### 1.6.2. Loại Biển và Kích Thước

**Loại biển theo màu sắc** [12], [13] giúp nhân viên bảo vệ nhanh chóng nhận diện loại phương tiện:

| Màu | Loại Phương Tiện | Mô Tả |
|-----|------------------|-------|
| Trắng | Ô tô cá nhân | Chữ đen trên nền trắng sáng, phổ biến nhất |
| Vàng | Ô tô kinh doanh vận tải, dịch vụ | Chữ đen trên nền vàng, xe kinh doanh (taxi, van) |
| Xanh | Xe máy cá nhân | Chữ trắng trên nền xanh, tất cả xe máy |
| Xanh đậm + Mã Tỉnh Trên | Phương tiện chính phủ, quân sự | Nền xanh đậm, chữ trắng |
| Đỏ | Đặc biệt (công an, quân đội) | Rất hiếm, chỉ các lực lượng đặc biệt |

**Kích thước biển** được chuẩn hóa:

**Ô tô 2 biển:**
- Biển ngắn (phía trước): 165 mm (cao) × 330 mm (rộng)
- Biển dài (phía sau): 110 mm (cao) × 520 mm (rộng)

**Xe máy 1 biển**: 110 mm (cao) × 200 mm (rộng)

**Biển 2 hàng** (xe máy, xe tải nhỏ): 110 mm (cao) × 200 mm (rộng), hàng 1 = mã tỉnh + chữ cái, hàng 2 = chữ số. Khoảng cách giữa hai hàng là cố định khoảng 15-20 mm.

Biển số là kim loại có lớp phản quang, được dập nổi các ký tự để tạo độ sâu và giúp nhìn rõ dưới đèn chiếu ban đêm. Nền biển trắng/vàng/xanh, ký tự màu đen (hoặc trắng cho xe máy), mặt phản quang giúp nhìn rõ vào buổi tối.

### 1.6.3. Font Chữ và Đặc Tính OCR

Ký tự trên biển số Việt Nam sử dụng font **Helvetica VN** hoặc **Font TT148** (do Bộ Công An định nghĩa chính thức), không phải font thường dùng trên máy tính. **Đặc điểm của font:**
- Ký tự có độ dày nhất định, không quá mảnh, dễ đọc ngay cả khi bẩn hoặc cũ.
- Khoảng cách giữa các ký tự cố định, dễ dàng phân đoạn (segmentation).
- Không có descender (phần nằm dưới baseline như ký tự 'g', 'p', 'q') nên dễ xác định vùng ký tự.

**Từ góc độ OCR**, những điểm lưu ý quan trọng:

1. **Biển 2 hàng**: Phải xác định mấy hàng biển, sắp xếp đúng thứ tự ký tự (hàng 1 → hàng 2). Nếu sắp xếp sai (ví dụ: số trước, chữ cái sau), kết quả sẽ hoàn toàn sai.

2. **Giãn cách**: Padding lề trên/dưới/trái/phải của biển nếu không chuẩn (ví dụ cắt quá sát ký tự, hoặc để thừa quá nhiều không) có thể làm sai kết quả.

3. **Mài mòn**: Biển cũ, ký tự bị mài mòn (mất một phần do va chạm, thời tiết), sẽ ảnh hưởng độ chính xác OCR.

4. **Góc chụp và ánh sáng**: Nếu góc lệch quá 15°, ký tự sẽ bị méo theo phối cảnh. Nếu ánh sáng quá sáng/tối, contrast sẽ xấu, khó nhận dạng.

**Nghiên cứu OCR cho biển Việt Nam** đã sử dụng dataset **VNLP (Vietnam License Plate detection and recognition)** gồm hơn 37,000 ảnh biển Việt Nam. Kết quả baseline: exact match ~37-55% tùy mô hình, character-level accuracy ~60-75%. Những con số này được xem là baseline, và cần fine-tuning hoặc post-processing để đạt >90% trong ứng dụng thực tế.

### 1.6.4. So Sánh với Biển Số Quốc Tế

Để hiểu tại sao mô hình OCR được huấn luyện trên biển quốc tế không thể áp dụng trực tiếp cho biển Việt Nam, bảng dưới so sánh:

| Đặc Tính | Việt Nam | EU | Hoa Kỳ | Trung Quốc |
|----------|---------|----|----|-----------|
| Mã Quốc Gia | Không | Có (trên trái) | Không | Không |
| Mã Tỉnh/Bang | 2 chữ số | 2 chữ cái | Thay đổi | 1 chữ cái |
| Format | Tỉnh-Chữ-Số | Chữ-Số-Chữ | Thay đổi | Chữ-Số-Chữ-Số |
| Số Ký Tự | 7-9 | 7-8 | 7 | 7-8 |
| Ký Tự | A-Z, 0-9 | A-Z, 0-9 | A-Z, 0-9 | Tiếng Trung, A-Z, 0-9 |
| Loại Phương Tiện | Màu biển | Loại kích thước | Loại state | Màu nền |

**Nhận xét quan trọng:** Những khác biệt này có ý nghĩa lớn với OCR. Mô hình được huấn luyện trên biển Hoa Kỳ (7 ký tự, format khác, font khác) **không thể áp dụng trực tiếp** cho biển Việt Nam (7-9 ký tự, format tỉnh-chữ-số, font Helvetica VN). Điều này yêu cầu **fine-tuning hoặc retraining** mô hình OCR cụ thể cho từng quốc gia hoặc region.

---

## Tóm Tắt Chương

Chương 1 đã trình bày cơ sở lý thuyết toàn diện cho hệ thống nhận diện biển số xe trong bối cảnh quản lý phương tiện tại cơ sở giáo dục. Các nội dung chính:

**1. Bài toán thực tế (1.1):** Quản lý thủ công hiện nay kém hiệu quả, dễ sai sót, không kịp cảnh báo. ANPR là công nghệ phù hợp, với thị trường toàn cầu phát triển nhanh 9%+ mỗi năm, ứng dụng rộng rãi ở quốc gia phát triển.

**2. ANPR là quy trình 4 giai đoạn (1.2):** Vehicle Detection → Plate Localization → Character Segmentation → OCR. Công nghệ phát triển từ truyền thống (edge detection) sang deep learning (multi-stage CNN) sang end-to-end (tích hợp). Thách thức chính: ánh sáng biến đổi, góc chụp, occlusion, motion blur, biển 2 hàng.

**3. YOLO là detector nhanh nhất (1.3):** YOLOv8n siêu nhẹ (3.2M param, 0.99ms), YOLOv8m chính xác cao (mAP 50%). Có thể dùng cho phát hiện phương tiện cũng như phát hiện từng ký tự OCR.

**4. SORT là tracker đơn giản mà hiệu quả (1.4):** Tốc độ 260 Hz, dùng Kalman Filter + Hungarian Assignment. Không cần training, dễ triển khai. ID switch có thể cải tiến bằng ByteTrack nếu cần.

**5. Công nghệ web hiện đại (1.5):** FastAPI (async backend), PostgreSQL (dữ liệu), React (dashboard), Docker (deployment). Kiến trúc mở rộng, dễ bảo trì.

**6. Biển số Việt Nam có đặc tính riêng (1.6):** Format 2-tỉnh + 1-2-chữ + 4-5-số, đa loại màu, 1-2 hàng, font Helvetica VN. Baseline OCR ~37-55% exact match, cần fine-tuning lên >90% trong thực tế.

Các lý thuyết trên là nền tảng kỹ thuật và tham khảo khoa học cho thiết kế chi tiết hệ thống, được trình bày ở các chương tiếp theo. Sự tích hợp giữa AI Engine, Backend, và Dashboard tạo nên một hệ thống hoàn chỉnh, từ capture video đến hiển thị kết quả người dùng cuối.

---

## Tài Liệu Tham Khảo

[1] Du, K., et al., "Automatic Number Plate Recognition (ANPR) in smart cities: A systematic review," *Computers, Environment and Urban Systems*, vol. 96, p. 101847, 2022.

[2] "Automatic Number Plate Recognition: A Detailed Survey of Relevant Algorithms," *Sensors*, vol. 21, no. 9, art. 3028, May 2022.

[3] "A Survey of Automatic Number Plate Recognition and Parking Management System," in *Proc. Smart Energy Computing*, Springer, 2024.

[4] "YOLOv8 vs. YOLOv5: A Comprehensive Technical Comparison," *Ultralytics YOLO Docs*, 2023.

[5] "Performance Comparison of YOLO Object Detection Models," *Learn OpenCV*, 2023.

[6] Zhu, Y., et al., "Performance Evaluation of YOLOv8 for Object Detection on the COCO Dataset," *Int. J. Res. Appl. Sci. Eng. Technol.*, vol. 12, 2024.

[7] "YOLOv5, YOLOv8 and YOLOv10: The Go-To Detectors for Real-time Vision," arXiv preprint arXiv:2407.02988, 2024.

[8] Bewley, A., Ge, Z., Ott, L., Ramos, F., and Upcroft, B., "Simple online and realtime tracking," in *2016 IEEE International Conference on Image Processing (ICIP)*, pp. 3464–3468, 2016.

[9] Bewley, A., et al., "Simple Online and Realtime Tracking," *arXiv preprint arXiv:1602.00763*, 2016.

[10] "ByteTrack: Multi-Object Tracking by Associating Every Detection Box," *arXiv preprint*, 2021.

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

**Ghi Chú cho Tác Giả:**

- [ ] Thêm các **HÌNH 1.1** - **1.6** (sơ đồ, biểu đồ, ảnh biển số mẫu) nếu cần
- [ ] Review lại ngôn ngữ, thêm chi tiết nếu cần
- [ ] Xác nhận độ dài (~6,000+ từ, 15-17 trang A4), nếu quá dài có thể rút gọn 1.5 hoặc 1.6
- [ ] Kiểm tra trích dẫn [N] khớp với danh sách References
- [ ] Nếu cần thêm phần khác (ví dụ: 1.7 về Xử Lý Dữ Liệu hay 1.8 về An Ninh/Pháp Lý), hãy thêm vào
