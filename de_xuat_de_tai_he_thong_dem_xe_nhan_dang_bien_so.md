ĐỀ XUẤT TÊN ĐỀ TÀI TỐT NGHIỆP, KHUNG NỘI DUNG
VÀ KẾ HOẠCH TRIỂN KHAI
Chủ đề nền tảng: Thiết kế hệ thống đếm phương tiện và nhận dạng biển số, có server nhận dữ liệu và dashboard thống kê.
Hướng nghiên cứu	Thị giác máy tính - Hệ thống giao thông thông minh - Web/Backend
Phiên bản	Bản đề xuất phục vụ thảo luận/chốt đề tài
 
I. Cơ sở định hướng và cách tiếp cận chốt đề tài
Lớp bài toán tổng thể: hệ thống giao thông thông minh (Intelligent Transportation System - ITS).
Bài toán kỹ thuật lõi: phát hiện phương tiện - theo dõi - đếm theo hướng/vùng - phát hiện biển số - OCR - hậu xử lý - gửi sự kiện về server - hiển thị realtime và thống kê.
Phạm vi ĐATN: xây dựng prototype end-to-end trên 1 hoặc vài kịch bản điển hình
II. Các hướng ứng dụng đề tài dự kiến
Dựa trên góp ý của thầy, chúng em dự định phát triển đề tài theo bốn hướng ứng dụng chính dưới đây. Mỗi hướng có ưu tiên nghiên cứu, dữ liệu, dashboard và độ khó khác nhau, hiện tại chúng em vẫn chưa quyết định:
Hướng	Bối cảnh ứng dụng	Mục tiêu trọng tâm	Ưu điểm	Lưu ý phạm vi
1	Đô thị/hỗn hợp	Đếm lưu lượng theo loại xe, theo khung giờ, theo hướng vào/ra tại nút/đoạn đường đô thị.	Sát thực tế Việt Nam; dữ liệu phong phú; dashboard đa dạng.	Độ khó cao do nhiều loại xe, che khuất, mật độ lớn.
2	Cao tốc/trạm kiểm soát	Giám sát xe ô tô, xe tải, bus; thống kê lưu lượng và biển số qua làn.	Bối cảnh rõ ràng, ít loại xe hơn, dễ chuẩn hóa luồng.	Ít tính tổng quát cho luồng hỗn hợp xe máy.
3	Kiểm soát ra/vào khu vực	Theo dõi phương tiện ra/vào cơ quan, khu dân cư, nhà máy, campus hoặc cổng thành phố.	Bài toán rõ, biển số có giá trị ứng dụng cao, dễ chốt KPI.	Cần thiết kế logic whitelist/blacklist hoặc lưu nhật ký truy vết.
4	Bãi đỗ xe thông minh	Đếm xe ra/vào, nhận dạng biển số, quản lý thời gian gửi xe và dashboard giám sát bãi.	Rất phù hợp với prototype; camera cố định; ít biến động góc chụp.	Ít phản ánh bài toán giao thông mở ngoài trời quy mô lớn.
Trong bốn hướng trên, phương án “kiểm soát phương tiện ra/vào khu vực” hoặc “bãi đỗ xe thông minh” thường phù hợp nhất để triển khai prototype hoàn chỉnh; trong khi phương án “đô thị/hỗn hợp” phù hợp hơn nếu mục tiêu là nhấn mạnh nghiên cứu thuật toán trong bối cảnh khó.
Bọn em định chọn “kiểm soát phương tiện ra/vào khu vực” hoặc “bãi đỗ xe thông minh”.
III. Đề xuất tên đề tài tốt nghiệp
Dưới đây là các phương án tên đề tài tương ứng với từng định hướng ứng dụng.
STT	Hướng	Tên đề tài đề xuất	Mức phù hợp
1	Kiểm soát ra/vào khu vực	Thiết kế và xây dựng hệ thống đếm phương tiện, nhận dạng biển số và quản lý phương tiện ra/vào khu vực giám sát	Rất phù hợp để làm prototype hoàn chỉnh
2	Bãi đỗ xe thông minh	Thiết kế hệ thống đếm phương tiện và nhận dạng biển số cho bài toán giám sát bãi đỗ xe thông minh	Rất khả thi, dễ đánh giá
Đề xuất ưu tiên để chốt với thầy:
1.	Tên ưu tiên 1: Thiết kế hệ thống đếm phương tiện, nhận dạng biển số và quản lý phương tiện ra/vào khu vực giám sát.
2.	Tên ưu tiên 2: Thiết kế hệ thống xử lý video đếm phương tiện và nhận dạng biển số, tích hợp server tiếp nhận dữ liệu và dashboard thống kê realtime.
3.	Tên ưu tiên 3: Thiết kế hệ thống đếm phương tiện và nhận dạng biển số cho bài toán giám sát bãi đỗ xe thông minh.
IV. Xác định phạm vi nghiên cứu và giới hạn bài toán trong khuôn khổ ĐATN
Để bảo đảm tính khả thi, đề tài nên được giới hạn theo nguyên tắc: chọn một bối cảnh triển khai điển hình, một số loại phương tiện mục tiêu và một kiến trúc prototype đủ thể hiện luồng dữ liệu end-to-end. Phạm vi chúng em đề xuất như sau:
•	Đầu vào: 01 hoặc nhiều luồng video/camera cố định; ưu tiên góc nhìn đủ quan sát phương tiện và biển số.
•	Đối tượng: tùy bối cảnh, có thể giới hạn ở ô tô - xe máy - xe tải nhẹ; không bắt buộc bao phủ toàn bộ phương tiện đặc biệt. Ví dụ: nếu chọn phạm vi trong trường thì chỉ có xe máy và xe đạp, còn nếu là video cố định ở một nút giao thông thì sẽ đa dạng hơn
•	Chức năng lõi: phát hiện phương tiện, theo dõi đối tượng, đếm theo hướng hoặc theo vùng, phát hiện biển số, OCR, hậu xử lý chuỗi ký tự, gửi sự kiện lên server và hiển thị dashboard.
•	Server/CSDL: lưu nhật ký sự kiện, ảnh chụp minh chứng, bản ghi biển số, thời gian, loại phương tiện
•	Dashboard: hiển thị realtime số lượt vào/ra, lưu lượng theo giờ/ngày, danh sách biển số gần nhất, tra cứu sự kiện, tỉ lệ nhận dạng thành công.
•	Không nhất thiết triển khai phần cứng hoàn chỉnh quy mô lớn; có thể dừng ở mức prototype phần mềm, hoặc bổ sung một mô hình phần cứng thử nghiệm nếu còn nguồn lực.
V. Khung nội dung dự kiến thực hiện (mục lục sơ bộ)
Khung nội dung dưới đây được xây dựng theo hướng một đồ án tốt nghiệp có đủ phần tổng quan, cơ sở lý thuyết, phân tích thiết kế hệ thống, triển khai, thực nghiệm và đánh giá.
Chương 1. Mở đầu
•	Lý do chọn đề tài
•	Bối cảnh và ý nghĩa ứng dụng trong hệ thống giao thông thông minh
•	Mục tiêu nghiên cứu
•	Đối tượng và phạm vi nghiên cứu
•	Phương pháp nghiên cứu
•	Bố cục đồ án
Chương 2. Tổng quan bài toán và công nghệ liên quan
•	Tổng quan hệ thống giao thông thông minh và các bài toán giám sát phương tiện
•	Các hướng ứng dụng: đô thị, cao tốc, cổng kiểm soát, bãi đỗ xe thông minh
•	Tổng quan các kỹ thuật phát hiện đối tượng, theo dõi đối tượng và nhận dạng biển số
•	Các công nghệ triển khai dự kiến: YOLO, tracking, OCR, OpenCV, FastAPI/Node.js, React, CSDL (PostgreSQL/MySQL)
Chương 3. Phân tích yêu cầu và thiết kế hệ thống
•	Mô tả bài toán và kịch bản vận hành
•	Yêu cầu chức năng và phi chức năng
•	Kiến trúc tổng thể hệ thống
•	Thiết kế module xử lý video/AI
•	Thiết kế backend API, server tiếp nhận sự kiện và CSDL
•	Thiết kế dashboard giám sát và thống kê
•	Thiết kế luồng dữ liệu giữa camera - AI engine - server - dashboard
Chương 4. Xây dựng module đếm phương tiện
•	Tiền xử lý video và cấu hình camera
•	Phát hiện phương tiện bằng mô hình học sâu
•	Theo dõi đối tượng giữa các khung hình
•	Thiết kế luật đếm theo line-crossing hoặc theo vùng
•	Xử lý các trường hợp đếm sai: che khuất, dừng lâu, quay đầu, mật độ cao
Chương 5. Xây dựng module nhận dạng biển số
•	Phát hiện vùng biển số
•	Cắt, hiệu chỉnh và nâng cao chất lượng ảnh biển số
•	Nhận dạng ký tự bằng OCR/mô hình học sâu
•	Hậu xử lý chuỗi biển số theo mẫu quy tắc
•	Đánh giá độ chính xác và phân tích lỗi
Chương 6. Xây dựng server, cơ sở dữ liệu và dashboard
•	Thiết kế API tiếp nhận dữ liệu/sự kiện
•	Thiết kế schema CSDL
•	Quản lý sự kiện phương tiện và ảnh minh chứng
•	Dashboard realtime: live events, counters, tra cứu biển số
•	Dashboard thống kê: lưu lượng theo thời gian, theo loại xe, danh sách biển số
Chương 7. Thực nghiệm và đánh giá
•	Mô tả bộ dữ liệu và kịch bản thử nghiệm
•	Các chỉ số đánh giá
•	Kết quả thực nghiệm cho từng module
•	Đánh giá tổng thể hệ thống
•	So sánh ưu/nhược điểm, các giới hạn còn tồn tại
Chương 8. Kết luận và hướng phát triển
•	Kết quả đạt được
•	Những hạn chế
•	Hướng mở rộng: nhiều camera, edge deployment, IoT, cảnh báo thông minh, tích hợp quản lý phương tiện
VI. Nội dung triển khai chi tiết
1. Hệ thống thu nhận ảnh/video và dữ liệu
•	Khảo sát nguồn dữ liệu: camera giao thông, camera cổng ra/vào, camera bãi xe, video tự thu thập hoặc bộ dữ liệu công khai.
•	Xây dựng quy trình lưu trữ video/frame, đặt tên dữ liệu và đồng bộ nhãn.
•	Tiền xử lý dữ liệu: trích frame, lọc khung hình hữu ích, gán nhãn phương tiện/biển số.
•	Tổ chức dữ liệu cho huấn luyện, kiểm thử và đánh giá.
2. Cơ sở dữ liệu biển số và dữ liệu nghiệp vụ
•	Thiết kế bảng lưu phương tiện, bản ghi biển số, nhật ký vào/ra, camera, người dùng hệ thống.
•	Quản lý ảnh biển số, chuỗi OCR, độ tin cậy nhận dạng
•	Mở rộng nghiệp vụ theo từng bối cảnh: danh sách xe được phép, xe vi phạm, thời gian gửi xe, thống kê theo ca/ngày.
3. Lựa chọn công cụ, thư viện và mô hình
•	Phương tiện/biển số: trước hết là YOLO (phiên bản bao nhiêu chúng em chua quyết định)
•	Tracking: ByteTrack, DeepSORT hoặc giải pháp tương đương.
•	OCR: PaddleOCR, CRNN, easyOCR hoặc giải pháp chuyên cho biển số.
•	Xử lý ảnh: OpenCV; huấn luyện/suy luận: PyTorch hoặc framework tương thích.
•	Backend: FastAPI hoặc Node.js; frontend dashboard: React; CSDL: PostgreSQL/MySQL
4. Các thông số hiển thị trên dashboard
•	Tổng số lượt xe vào/ra theo ngày (tuần, tháng).
•	Lưu lượng theo khung giờ, theo camera, theo loại phương tiện.
•	Danh sách biển số mới nhất, ảnh chụp minh chứng, thời điểm ghi nhận, trạng thái nhận dạng.
•	Tỉ lệ nhận dạng thành công, số trường hợp không đọc được biển số, FPS hoặc độ trễ hệ thống.
•	Tra cứu theo biển số, khoảng thời gian (theo thời gian thực hoặc thời điểm trong video)
5. Thách thức và hướng giải quyết
•	Luồng xe hỗn hợp trong cùng khung hình: cần tập dữ liệu đa dạng và luật đếm ổn định.
•	Điều kiện ngày/đêm, mưa, ngược sáng: cần tăng cường dữ liệu hoặc tiền xử lý phù hợp.
•	Biển số mờ, bẩn, che khuất: cần bước chọn frame tốt nhất, deblur/căn chỉnh và hậu xử lý.
•	Che khuất giữa nhiều xe: cần tracking tốt để tránh đếm sai và chọn đúng ảnh biển số.
•	Góc nghiêng camera: cần hiệu chỉnh phối cảnh/rotation trước OCR.
•	Xử lý thời gian thực: tối ưu mô hình, pipeline song song và cơ chế gửi sự kiện.
VII. Kiến trúc hệ thống đề xuất
Một kiến trúc phù hợp cho ĐATN có thể gồm 4 lớp chính:
Lớp	Thành phần	Dữ liệu vào/ra	Vai trò
1. Camera/Input	Camera IP, webcam, video file	Khung hình/video stream	Cung cấp dữ liệu ảnh/video cho bộ xử lý
2. AI Engine	Detector phương tiện, tracker, detector biển số, OCR, hậu xử lý	Frame vào - sự kiện/ảnh biển số ra	Suy luận realtime, sinh sự kiện đếm và nhận dạng
3. Backend + DB	API server, message/event handler, CSDL	Sự kiện vào - bản ghi/log ra	Lưu trữ, quản trị, cung cấp dữ liệu cho dashboard
4. Dashboard	Web giao diện quản trị và thống kê	Dữ liệu realtime/lịch sử	Giám sát, tra cứu, hiển thị biểu đồ và danh sách biển số
VIII. Chỉ tiêu đầu ra và tiêu chí đánh giá

Nhóm	Mô tả	Ghi chú
Đếm phương tiện	So sánh số đếm hệ thống với nhãn thực tế theo video/kịch bản.	Có thể đánh giá theo từng hướng (vào/ra)
Phát hiện	Đánh giá phát hiện phương tiện và biển số.	Tùy mức dữ liệu gán nhãn.
Tracking	Đánh giá độ ổn định bám theo đối tượng.	Có thể giản lược nếu tập trung vào độ chính xác đếm.
Biển số	Đánh giá đúng sai chuỗi ký tự nhận dạng.	Nên kèm phân tích lỗi theo điều kiện ánh sáng/góc chụp.
Hệ thống	Đánh giá khả năng chạy realtime/near realtime.	Đo trên cấu hình thử nghiệm cụ thể.
Dashboard	Hiển thị đúng dữ liệu realtime, tra cứu và thống kê.	Đánh giá bằng checklist chức năng.
IX. Kế hoạch và tiến độ triển khai đề xuất
Tiến độ dưới đây được xây dựng theo logic: chốt phạm vi trước, hoàn thiện pipeline đếm xe trước, sau đó tích hợp nhận dạng biển số, cuối cùng mới hoàn thiện backend, CSDL và dashboard. 
Giai đoạn	Mục tiêu	Công việc chính	Sản phẩm đầu ra
1. Khảo sát và chốt đề tài	Chốt bối cảnh ứng dụng, tên đề tài, phạm vi	Tổng quan tài liệu; khảo sát dữ liệu; chọn hướng ứng dụng; xác định KPI và kiến trúc sơ bộ	Đề cương/outline và kế hoạch được duyệt
2. Chuẩn bị dữ liệu và baseline	Có dữ liệu thử nghiệm và pipeline cơ sở	Thu thập video; trích frame; gán nhãn một phần; chạy mô hình detect baseline	Bộ dữ liệu ban đầu và kết quả baseline
3. Xây dựng module đếm phương tiện	Đếm ổn định theo line/vùng	Huấn luyện/tinh chỉnh detector; tích hợp tracker; xây luật đếm; đánh giá sai số	Module đếm xe hoạt động trên video thử nghiệm
4. Xây dựng module nhận dạng biển số	Đọc được biển số với độ chính xác chấp nhận được	Detect biển số; crop/căn chỉnh; OCR; hậu xử lý theo mẫu biển số	Module LPR/OCR và báo cáo đánh giá
5. Backend, CSDL và API	Có server tiếp nhận sự kiện và lưu trữ dữ liệu	Thiết kế API; schema DB; lưu event, ảnh, biển số; test truy vấn	Backend + CSDL hoạt động ổn định
6. Dashboard realtime và thống kê	Hiển thị realtime và báo cáo cơ bản	Thiết kế giao diện; biểu đồ; bảng sự kiện; tra cứu biển số; tích hợp API	Dashboard web hoàn chỉnh bản đầu
7. Tích hợp, tối ưu và kiểm thử	Hệ thống end-to-end ổn định	Kiểm thử các kịch bản; tối ưu tốc độ; sửa lỗi; hoàn thiện demo	Prototype hoàn chỉnh và video demo
8. Viết báo cáo và chuẩn bị bảo vệ	Hoàn thiện hồ sơ đồ án	Viết báo cáo; chuẩn hóa hình bảng; chuẩn bị slide và demo	Báo cáo, slide, demo bảo vệ
Tiến độ chi tiết theo 16 tuần:
Tuần	Nội dung chính	Kết quả cần đạt
1-2	Khảo sát tài liệu, chốt hướng ứng dụng, tên đề tài, phạm vi và KPI	Có đề cương chi tiết được thống nhất
3-4	Chuẩn bị dữ liệu, thử nghiệm detector phương tiện và pipeline đọc video	Chạy được baseline detect trên video
5-6	Tích hợp tracking, thiết kế luật đếm theo line/vùng, đo sai số đếm	Module đếm xe có kết quả sơ bộ
7-8	Xây dựng phát hiện biển số, crop/căn chỉnh và OCR ban đầu	Đọc được biển số trong điều kiện thuận lợi
9-10	Hậu xử lý OCR, đánh giá lỗi, tối ưu độ chính xác	Bộ nhận dạng biển số ổn định hơn
11-12	Thiết kế backend, CSDL, API tiếp nhận sự kiện	Có server và DB lưu được dữ liệu
13-14	Xây dựng dashboard realtime/thống kê, kết nối với backend	Dashboard xem được dữ liệu thực tế
15	Tích hợp tổng thể, tối ưu, kiểm thử theo kịch bản	Prototype end-to-end hoàn chỉnh
16	Viết báo cáo, hoàn thiện slide, video demo và chuẩn bị bảo vệ	Hồ sơ bảo vệ hoàn chỉnh
X. Rủi ro thực hiện và phương án dự phòng
•	Nếu dữ liệu thực tế khó thu thập hoặc chất lượng thấp, có thể dùng bộ dữ liệu công khai kết hợp video tự quay để minh họa.
•	Nếu không đủ thời gian tối ưu mọi chỉ số, cần ưu tiên hoàn thiện luồng end-to-end có thể demo được và có số liệu đánh giá rõ ràng.
•	Xem xét cắt bớt các chức năng nếu thời gian tổng thể không đủ

