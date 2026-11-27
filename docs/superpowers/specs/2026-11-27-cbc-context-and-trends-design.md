# Thiết kế: Bối cảnh kết quả và theo dõi CBC theo thời gian

## Ý định

Giúp người dùng hiểu phiếu CBC của chính mình, biết những thay đổi nào đáng đưa ra trao đổi tại buổi khám, và chuẩn bị câu hỏi cụ thể. Sản phẩm không đưa ra chẩn đoán, đánh giá mức độ nguy hiểm hoặc hướng điều trị.

## Mục tiêu

- Hiển thị ngày lấy mẫu do người dùng xác nhận trên từng phiếu.
- Cho phép xem các phiếu CBC đã xác nhận thuộc chính tài khoản và so sánh với phiếu trước.
- Với từng chỉ số có ở cả hai phiếu, trình bày giá trị trước/sau, chênh lệch số học khi đơn vị có thể quy đổi an toàn, và trạng thái so với khoảng tham chiếu của từng phiếu.
- Nêu rõ khi không thể so sánh trực tiếp vì thiếu ngày, thiếu chỉ số, đơn vị không tương thích, hoặc khác nguồn/khoảng tham chiếu.
- Tạo gợi ý câu hỏi ngắn, có nhắc tên chỉ số và kết quả hiện tại, để người dùng mang tới buổi khám.
- Giữ dữ liệu phiếu riêng tư theo tài khoản và cho phép xóa phiếu.

## Ngoài phạm vi

- Không suy luận nguyên nhân bệnh từ CBC, đưa mức độ khẩn cấp, chẩn đoán, hoặc gợi ý thuốc/điều trị.
- Không mô tả xu hướng tăng/giảm là tốt lên hay xấu đi.
- Không dùng LLM để tính toán, xác định bất thường, hoặc tự viết diễn giải lâm sàng.
- Không tự động đọc ngày xét nghiệm từ ảnh OCR; người dùng xác nhận ngày.
- Không thay đổi khoảng tham chiếu, dữ liệu nghiên cứu, chuẩn hóa đơn vị hiện hành hoặc công thức phân loại.

## Các hướng đã cân nhắc

- **Diễn giải y khoa sâu từ một phiếu:** linh hoạt nhưng CBC đơn lẻ thiếu triệu chứng, tiền sử và xét nghiệm liên quan; có nguy cơ khiến người dùng nhầm giải thích thành chẩn đoán.
- **Theo dõi dữ liệu đã xác nhận và gợi ý câu hỏi có căn cứ vào phiếu:** tận dụng các giá trị/ngày/khoảng có sẵn, làm rõ khác biệt giữa hai lần đo, không suy diễn bệnh. Chọn hướng này vì an toàn và trực tiếp giúp người dùng chuẩn bị buổi khám.

## Thiết kế hành vi

- Phiếu mới có trường “Ngày lấy mẫu” (ngày ghi trên phiếu); không mặc định ngày tạo phiên là ngày lấy mẫu.
- Danh sách lịch sử chỉ trả về các phiên có báo cáo đã xác nhận thuộc người dùng hiện tại. Người dùng chọn một phiếu trước đó để so sánh; không tự chọn dữ liệu của tài khoản khác.
- So sánh giá trị chỉ khi mã chỉ số trùng và đơn vị đã được chuẩn hóa về cùng đơn vị bởi logic hiện có. Nếu không, hiển thị lý do không so sánh.
- Trạng thái tham chiếu của mỗi ngày dùng khoảng đã được lưu với phiếu đó. Giao diện không gộp hai khoảng khác nguồn hoặc khác giai đoạn thành một kết luận.
- Kết quả dùng ngôn ngữ trung tính: “giá trị thay đổi từ … sang …”; nếu khoảng tham chiếu khác, ghi rõ trạng thái hai ngày đang dùng khoảng riêng của từng phiếu.
- Gợi ý hỏi bác sĩ là câu hỏi, không phải kết luận; ví dụ hỏi bác sĩ cần xem chỉ số cụ thể cùng tuổi thai/triệu chứng/thông tin nào.
- Thông tin riêng tư: API truy vấn lịch sử luôn lọc theo `owner_id`; xóa phiên xóa báo cáo liên quan theo cơ chế hiện có.

## Thành phần dự kiến

- API: xác thực và trả danh sách báo cáo đã xác nhận của người dùng; xác nhận ngày lấy mẫu; trả dữ liệu so sánh với một phiên do người dùng chọn.
- SQLite: lưu ngày lấy mẫu theo phiên, tương thích với các bản ghi cũ chưa có ngày.
- Giao diện: nhập ngày trên phiếu, mở lịch sử cá nhân, chọn lần đo cũ, xem bảng so sánh và câu hỏi gợi ý.
- Kiểm tra đầu vào: ngày hợp lệ; không chấp nhận ngày tương lai; không để dữ liệu phiên khác người dùng lọt vào phản hồi.

## Tiêu chí hoàn thành

- Người dùng có thể xác nhận nhiều phiếu với ngày lấy mẫu riêng và xem lịch sử của mình.
- So sánh cùng chỉ số trình bày trung tính, không diễn giải tăng/giảm thành tình trạng sức khỏe.
- Phiếu cũ thiếu ngày và các cặp đơn vị không tương thích được chỉ rõ là chưa thể so sánh.
- Gợi ý câu hỏi nói đến chỉ số thực có trên phiếu, không tạo bệnh, nguyên nhân hay điều trị.
- Các tuyến API không trả phiếu của người dùng khác.
