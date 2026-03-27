


BÁO CÁO ĐỀ XUẤT ĐỀ TÀI TỐT NGHIỆP
THIẾT KẾ HỆ THỐNG QUẢN LÝ PHƯƠNG TIỆN RA/VÀO
ĐẠI HỌC BÁCH KHOA HÀ NỘI THÔNG QUA NHẬN DIỆN BIỂN SỐ XE






 
MỞ ĐẦU
Trong bối cảnh chuyển đổi số tại các cơ sở giáo dục đào tạo, việc quản lý phương tiện ra/vào khuôn viên trường không chỉ dừng ở yêu cầu kiểm soát an ninh mà còn gắn với tối ưu vận hành, giảm áp lực cho lực lượng bảo vệ, hỗ trợ điều tiết lưu lượng trong giờ cao điểm và hình thành dữ liệu phục vụ quản trị nhà trường. Đối với môi trường đại học có mật độ người học lớn, dòng phương tiện thường mang tính hỗn hợp, thay đổi mạnh theo khung giờ và chịu ảnh hưởng rõ rệt của điều kiện ánh sáng, thời tiết cũng như đặc thù từng cổng ra/vào.
Báo cáo này được chỉnh sửa theo hướng thu hẹp phạm vi bài toán vào bối cảnh Đại học Bách khoa Hà Nội; đồng thời nhấn mạnh ba nội dung cốt lõi: xác định rõ đối tượng quản lý, mô hình hóa các nhóm cổng và luồng dữ liệu từ camera, và đề xuất năng lực hệ thống đủ cho quy mô khoảng 100.000 đầu phương tiện đăng ký. Trên cơ sở đó, tài liệu trình bày kiến trúc tổng thể, các mô-đun chức năng chính, tiêu chí đánh giá và định hướng phát triển của hệ thống.
Chương 1. Tổng quan về bài toán quản lý phương tiện thông qua nhận diện biển số xe
1.1. Bối cảnh bài toán tại cơ sở giáo dục đào tạo
So với nhiều bài toán giám sát giao thông đô thị, bài toán quản lý phương tiện trong trường đại học có đặc điểm riêng: mật độ xe máy rất cao, tần suất phát sinh theo các phiên học, dòng phương tiện không đồng đều giữa các cổng và xuất hiện đồng thời nhiều nhóm người dùng như cán bộ, sinh viên, khách đến liên hệ công tác, phương tiện dịch vụ hoặc phương tiện vào bãi xe ngắn hạn. Do đó, hệ thống cần vừa bảo đảm tốc độ xử lý gần thời gian thực, vừa duy trì độ chính xác đủ cao để phục vụ kiểm soát, thống kê và truy vết sự kiện khi cần thiết.
Nhận diện biển số xe được xem là hạt nhân của giải pháp vì cho phép liên kết sự kiện ghi nhận từ camera với hồ sơ phương tiện, từ đó hỗ trợ các nghiệp vụ như đối soát phương tiện đã đăng ký, phân loại đối tượng, ghi nhận lịch sử vào/ra, thống kê lưu lượng và cảnh báo đối với các trường hợp bất thường. Trên thực tế triển khai, mô-đun nhận diện biển số cần phối hợp chặt chẽ với mô-đun phát hiện phương tiện, theo dõi đối tượng và luật đếm theo hướng hoặc theo vùng để giảm hiện tượng đếm trùng hay nhận dạng sai trong dòng phương tiện hỗn hợp.
1.2. Cụ thể hóa bài toán tại Đại học Bách khoa Hà Nội
Trong khuôn khổ báo cáo, Đại học Bách khoa Hà Nội được lựa chọn như một kịch bản triển khai điển hình cho cơ sở giáo dục đào tạo có mật độ sử dụng phương tiện lớn. Mục tiêu của hệ thống là tự động ghi nhận phương tiện ra/vào tại các điểm kiểm soát điển hình trong khuôn viên trường, nhận diện biển số xe, phân loại theo nhóm đối tượng, lưu trữ nhật ký sự kiện và cung cấp dashboard theo dõi cho đơn vị quản lý. Kết quả đầu ra kỳ vọng không chỉ phục vụ công tác kiểm soát cổng, mà còn hỗ trợ đánh giá lưu lượng theo khung giờ, tối ưu vận hành bãi xe và nâng cao khả năng truy xuất dữ liệu khi phát sinh sự cố.
1.3. Đối tượng quản lý và phạm vi áp dụng
Bảng 1. Phân loại đối tượng quản lý và yêu cầu xử lý nghiệp vụ
Nhóm đối tượng	Phương tiện phổ biến	Đặc điểm vận hành	Yêu cầu xử lý chính
Cán bộ, giảng viên	Ô tô, xe máy	Ra/vào tương đối ổn định, ưu tiên khu vực nội bộ hoặc bãi xe chuyên dụng	Kiểm tra phương tiện đã đăng ký; lưu lịch sử vào/ra; thống kê theo đơn vị hoặc khu vực
Sinh viên	Chủ yếu xe máy, một phần ô tô	Lưu lượng cao, tập trung mạnh vào đầu giờ và cuối buổi học	Xử lý dòng hỗn hợp mật độ lớn; chống đếm trùng; tra cứu lịch sử theo biển số và thời gian
Phạm vi của đề tài được xác định theo hướng thiết kế và thử nghiệm hệ thống cho một số nhóm cổng tiêu biểu, thay vì triển khai đồng thời trên toàn bộ khuôn viên trường. Việc thu hẹp phạm vi như vậy giúp làm rõ yêu cầu kỹ thuật, kiểm soát khối lượng dữ liệu và đánh giá tính khả thi của giải pháp trước khi xem xét mở rộng ở giai đoạn tiếp theo.
Chương 2. Thiết kế hệ thống quản lý phương tiện ra vào trường Đại học Bách khoa Hà Nội
2.1. Xác định phạm vi nghiên cứu và giới hạn bài toán trong khuôn khổ ĐATN
Để bảo đảm tính khả thi, đề tài nên được giới hạn theo nguyên tắc: chọn một bối cảnh triển khai điển hình, một số loại phương tiện mục tiêu và một kiến trúc prototype đủ thể hiện luồng dữ liệu end-to-end. Phạm vi chúng em đề xuất như sau:
•	Đầu vào: 01 hoặc nhiều luồng video/camera cố định; ưu tiên góc nhìn đủ quan sát phương tiện và biển số.
•	Đối tượng: tùy bối cảnh, có thể giới hạn ở ô tô - xe máy - xe tải nhẹ; không bắt buộc bao phủ toàn bộ phương tiện đặc biệt. Ví dụ: nếu chọn phạm vi trong trường thì chỉ có xe máy và xe đạp, còn nếu là video cố định ở một nút giao thông thì sẽ đa dạng hơn
•	Chức năng lõi: phát hiện phương tiện, theo dõi đối tượng, đếm theo hướng hoặc theo vùng, phát hiện biển số, OCR, hậu xử lý chuỗi ký tự, gửi sự kiện lên server và hiển thị dashboard.
•	Server/CSDL: lưu nhật ký sự kiện, ảnh chụp minh chứng, bản ghi biển số, thời gian, loại phương tiện
•	Dashboard: hiển thị realtime số lượt vào/ra, lưu lượng theo giờ/ngày, danh sách biển số gần nhất, tra cứu sự kiện, tỉ lệ nhận dạng thành công.
•	Không nhất thiết triển khai phần cứng hoàn chỉnh quy mô lớn; có thể dừng ở mức prototype phần mềm, hoặc bổ sung một mô hình phần cứng thử nghiệm nếu còn nguồn lực.

2.2. Khung nội dung dự kiến thực hiện (mục lục sơ bộ)
Khung nội dung dưới đây được xây dựng theo hướng một đồ án tốt nghiệp có đủ phần tổng quan, cơ sở lý thuyết, phân tích thiết kế hệ thống, triển khai, thực nghiệm và đánh giá.
Chương 1. Mở đầu
Lý do chọn đề tài
Bối cảnh và ý nghĩa ứng dụng trong hệ thống giao thông thông minh
Mục tiêu nghiên cứu
Đối tượng và phạm vi nghiên cứu
Phương pháp nghiên cứu
Bố cục đồ án
Chương 2. Tổng quan bài toán và công nghệ liên quan
Tổng quan hệ thống giao thông thông minh và các bài toán giám sát phương tiện
Các hướng ứng dụng: đô thị, cao tốc, cổng kiểm soát, bãi đỗ xe thông minh
Tổng quan các kỹ thuật phát hiện đối tượng, theo dõi đối tượng và nhận dạng biển số
Các công nghệ triển khai dự kiến: YOLO, tracking, OCR, OpenCV, FastAPI/Node.js, React, CSDL (PostgreSQL/MySQL)
Chương 3. Phân tích yêu cầu và thiết kế hệ thống
Mô tả bài toán và kịch bản vận hành
Yêu cầu chức năng và phi chức năng
Kiến trúc tổng thể hệ thống
Thiết kế module xử lý video/AI
Thiết kế backend API, server tiếp nhận sự kiện và CSDL
Thiết kế dashboard giám sát và thống kê
Thiết kế luồng dữ liệu giữa camera - AI engine - server - dashboard
Chương 4. Xây dựng module đếm phương tiện
Tiền xử lý video và cấu hình camera
Phát hiện phương tiện bằng mô hình học sâu
Theo dõi đối tượng giữa các khung hình
Thiết kế luật đếm theo line-crossing hoặc theo vùng
Xử lý các trường hợp đếm sai: che khuất, dừng lâu, quay đầu, mật độ cao
Chương 5. Xây dựng module nhận dạng biển số
Phát hiện vùng biển số
Cắt, hiệu chỉnh và nâng cao chất lượng ảnh biển số
Nhận dạng ký tự bằng OCR/mô hình học sâu
Hậu xử lý chuỗi biển số theo mẫu quy tắc
Đánh giá độ chính xác và phân tích lỗi
Chương 6. Xây dựng server, cơ sở dữ liệu và dashboard
Thiết kế API tiếp nhận dữ liệu/sự kiện
Thiết kế schema CSDL
Quản lý sự kiện phương tiện và ảnh minh chứng
Dashboard realtime: live events, counters, tra cứu biển số
Dashboard thống kê: lưu lượng theo thời gian, theo loại xe, danh sách biển số
Chương 7. Thực nghiệm và đánh giá
Mô tả bộ dữ liệu và kịch bản thử nghiệm
Các chỉ số đánh giá
Kết quả thực nghiệm cho từng module
Đánh giá tổng thể hệ thống
So sánh ưu/nhược điểm, các giới hạn còn tồn tại
Chương 8. Kết luận và hướng phát triển
Kết quả đạt được
Những hạn chế
Hướng mở rộng: nhiều camera, edge deployment, IoT, cảnh báo thông minh, tích hợp quản lý phương tiện

2.3. Nội dung triển khai chi tiết
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

Chương 3. Đánh giá kết quả hệ thống và hướng phát triển
3.1. Kịch bản dữ liệu và thử nghiệm
Đánh giá hệ thống cần dựa trên các kịch bản phản ánh tương đối đầy đủ đặc trưng vận hành tại trường đại học, bao gồm giờ cao điểm sinh viên, luồng hỗn hợp ô tô - xe máy, điều kiện ánh sáng thay đổi, và trường hợp biển số bị che khuất một phần. Dữ liệu thử nghiệm có thể được thu thập từ camera thực tế tại một số điểm kiểm soát điển hình hoặc từ video mô phỏng bám sát điều kiện triển khai.
3.2. Bộ chỉ tiêu đánh giá
Bảng 2. Nhóm chỉ tiêu đánh giá hệ thống
Nhóm chỉ tiêu	Nội dung đánh giá	Ý nghĩa
Độ chính xác đếm	So sánh số lượt xe vào/ra do hệ thống ghi nhận với kết quả gán nhãn hoặc kiểm đếm tham chiếu	Phản ánh mức độ phù hợp của mô-đun phát hiện, tracking và luật đếm
Độ chính xác nhận diện biển số	Đo tỷ lệ biển số được nhận đúng hoàn toàn hoặc đúng một phần theo tiêu chí định trước	Là chỉ tiêu cốt lõi quyết định giá trị ứng dụng của hệ thống
Độ trễ xử lý	Tính thời gian từ khi phát sinh sự kiện tại camera đến khi hiển thị trên dashboard	Đánh giá khả năng vận hành gần thời gian thực
Độ ổn định vận hành	Theo dõi tỷ lệ mất khung hình, mất kết nối, lỗi OCR hoặc lỗi ghi nhận sự kiện	Phản ánh mức độ sẵn sàng khi triển khai ngoài hiện trường
Chất lượng dữ liệu quản trị	Kiểm tra tính đầy đủ của nhật ký, ảnh minh chứng và khả năng truy vấn báo cáo	Đánh giá mức độ hữu ích của hệ thống đối với công tác quản lý
3.3. Kết quả kỳ vọng và giá trị ứng dụng
Nếu được thiết kế và cấu hình phù hợp, hệ thống có thể hỗ trợ đáng kể cho công tác quản lý phương tiện trong trường: giảm phụ thuộc vào ghi chép thủ công, nâng cao tốc độ đối soát phương tiện, cung cấp dữ liệu lưu lượng phục vụ điều hành cổng và tạo nền tảng cho các chức năng quản trị nâng cao. Về mặt học thuật, đề tài cũng cho phép đánh giá hiệu quả phối hợp giữa các mô-đun phát hiện, tracking, OCR và quản trị dữ liệu trong một bài toán thị giác máy tính có giá trị ứng dụng rõ ràng.
3.4. Kế hoạch triển khai dự kiến trong 16 tuần
Bảng 3. Tiến độ thực hiện đề xuất
Tuần	Nội dung chính	Kết quả đầu ra
1-2	Khảo sát bài toán, rà soát tài liệu, chốt phạm vi và kịch bản áp dụng tại Đại học Bách khoa Hà Nội	Đề cương chi tiết và danh mục yêu cầu hệ thống
3-4	Thiết kế luồng dữ liệu, đặc tả nghiệp vụ, chuẩn bị dữ liệu hoặc video thử nghiệm	Tài liệu đặc tả và bộ dữ liệu ban đầu
5-7	Xây dựng mô-đun phát hiện phương tiện, tracking và luật đếm	Nguyên mẫu mô-đun đếm phương tiện
8-10	Xây dựng mô-đun phát hiện biển số, OCR và hậu xử lý	Nguyên mẫu mô-đun nhận diện biển số
11-12	Thiết kế backend, cơ sở dữ liệu và API tiếp nhận sự kiện	Hệ thống lưu trữ và dịch vụ tích hợp cơ bản
13-14	Phát triển dashboard, chức năng tra cứu và thống kê	Giao diện giám sát và báo cáo thử nghiệm
15	Đánh giá hệ thống theo bộ chỉ tiêu đã xây dựng	Bảng kết quả đánh giá và phân tích
16	Hoàn thiện báo cáo, chỉnh sửa trình bày và chuẩn bị bảo vệ	Báo cáo hoàn chỉnh và bản trình bày tóm tắt
3.5. Hướng phát triển
•	Mở rộng hệ thống cho nhiều camera và nhiều nhóm cổng, kết hợp xử lý edge để giảm tải đường truyền và tăng tính linh hoạt triển khai.
•	Tích hợp sâu hơn với quy trình đăng ký phương tiện của nhà trường, bao gồm danh sách phương tiện thường trú, quyền truy cập tạm thời và cơ chế phê duyệt điện tử.
•	Bổ sung chức năng cảnh báo thông minh cho các trường hợp phương tiện lạ, biển số có độ tin cậy thấp, lưu lượng bất thường hoặc vi phạm quy định ra/vào.
•	Nghiên cứu tối ưu mô hình nhận dạng biển số cho điều kiện ánh sáng phức tạp và tỷ lệ che khuất cao, đặc biệt đối với xe máy trong dòng hỗn hợp dày.
KẾT LUẬN
Bản hoàn thiện này đã chuyển báo cáo từ mô tả khái quát sang một đề xuất có bối cảnh áp dụng rõ ràng tại Đại học Bách khoa Hà Nội. Các nội dung trọng tâm đã được cụ thể hóa, bao gồm: xác định đối tượng quản lý là ô tô, xe máy của cán bộ, sinh viên và khách; mô hình hóa nhóm cổng/luồng ra vào; mô tả luồng dữ liệu từ camera; đặt mục tiêu quy mô cơ sở dữ liệu khoảng 100.000 đầu phương tiện.
Trên nền tảng đó, đề tài có thể tiếp tục được phát triển thành một hướng nghiên cứu và triển khai khả thi, vừa mang giá trị học thuật ở khía cạnh thị giác máy tính và thiết kế hệ thống, vừa có ý nghĩa thực tiễn đối với bài toán quản lý vận hành trong các cơ sở giáo dục đào tạo quy mô lớn.
