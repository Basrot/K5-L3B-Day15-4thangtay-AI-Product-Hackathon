# Thiết kế: CBC Care Companion cho mẹ bầu và bác sĩ

## Mục đích

Biến bản demo đối chiếu CBC thành công cụ giúp mẹ bầu hiểu phiếu của chính mình, theo dõi các lần xét nghiệm và chuẩn bị trao đổi ngắn gọn với bác sĩ. Sản phẩm không chẩn đoán, kê thuốc hoặc thay thế quyết định của bác sĩ.

## Hiện trạng và khoảng trống

- Có nhập tay/đọc ảnh, xác nhận dữ liệu, đối chiếu chỉ số, lịch sử và so sánh hai phiếu, hỏi đáp theo phiếu, âm thanh, câu hỏi cho bác sĩ.
- AI hiện chủ yếu nhận diện ý định; phần diễn giải là nội dung có kiểm soát. Điều này an toàn hơn nhưng còn nghèo ngữ cảnh và khiến sản phẩm giống trang tra cứu khoảng tham chiếu.
- Chưa có bản bàn giao buổi khám rõ ràng, tóm tắt xu hướng dễ đọc, hoặc khu vực bác sĩ xác nhận/ghi chú.

## Các phương án

1. **LLM tự viết chẩn đoán linh hoạt:** câu trả lời sinh động nhưng có thể khẳng định nguyên nhân hoặc điều trị vượt quá dữ liệu CBC; không chọn.
2. **Giữ chatbot phân loại câu hỏi và các câu mẫu đơn lẻ:** an toàn, nhưng không giải quyết khoảng trống về nhiều chỉ số và lịch sử; không chọn làm đích cuối.
3. **AI hỗ trợ diễn giải có nguồn, mẫu kiểm soát, theo dữ liệu đã xác nhận (chọn):** định tuyến câu hỏi và nhận diện nhóm/ý định; logic có kiểm tra xác định các giá trị, trạng thái và xu hướng; câu trả lời có giới hạn, nguồn và câu hỏi gợi ý. Xuất bản tóm tắt có thể in hoặc mang tới buổi khám. Cách này mở rộng theo kiến trúc hiện tại và giữ kết luận lâm sàng cho bác sĩ.

## Trải nghiệm chính

1. Người dùng chụp phiếu hoặc nhập số, xem lại giá trị/đơn vị/tuổi thai rồi xác nhận.
2. Trang kết quả nêu các dòng đã đối chiếu, nhóm chỉ số cần bàn thêm, ý nghĩa chung có thể rút ra, điều CBC chưa thể kết luận, và câu hỏi nên trao đổi.
3. Trợ lý nhận câu hỏi tự nhiên về một dòng hoặc một nhóm dòng trong phiếu đã xác nhận; câu trả lời nêu giá trị chính xác, khoảng đã dùng, nguồn và giới hạn.
4. So sánh phiếu cũ/mới làm nổi bật thay đổi số liệu và trạng thái theo từng khoảng, không gọi tăng/giảm là cải thiện/xấu đi.
5. “Tóm tắt buổi khám” tạo trang in/tải xuống ngắn gọn gồm tuổi thai/ngày lấy mẫu nếu có, nguồn khoảng, giá trị và trạng thái, các điểm nên hỏi và nguồn tham khảo.

## Vai trò và giới hạn

- Bệnh nhân dùng để đọc phiếu và chuẩn bị câu hỏi.
- Bác sĩ nhận bản tóm tắt do bệnh nhân chủ động mang tới; đợt này không tạo tài khoản bác sĩ hay chia sẻ phiếu công khai.
- Chỉ dùng dữ liệu đã xác nhận cho giải thích AI và bản tóm tắt. Dữ liệu OCR chưa xác nhận không được xem là kết quả thật.
- Không tạo chẩn đoán, xác suất bệnh, mức độ khẩn cấp từ trạng thái tham chiếu đơn thuần, hoặc khuyến nghị thuốc.
- Không thay đổi thuật toán, các khoảng nghiên cứu, đơn vị, quyền sở hữu hay hợp đồng API hiện có nếu không cần thiết.
- Câu trả lời giữ mẫu kiểm soát đã được người dùng chốt trước đó; LLM không tự viết nội dung y khoa tự do.

## Nội dung y khoa

- Mỗi giải thích phải tách “đang thấp/cao theo khoảng đã chọn” khỏi “có bệnh”.
- HGB/RBC/HCT/MCV/MCH/MCHC được xem như nhóm hồng cầu; WBC và PLT được giải thích riêng. Các kiểu kết quả chỉ là lý do để bác sĩ xem thêm, không chỉ ra nguyên nhân duy nhất.
- Nêu rõ hạn chế của nghiên cứu tham chiếu trong thai kỳ và khi cần thì dẫn nguồn của chính khoảng đang dùng cùng nguồn giáo dục y khoa phù hợp.
- Xu hướng theo thời gian chỉ mô tả thay đổi số và trạng thái; không tự gọi đó là tiến triển bệnh hoặc đáp ứng điều trị.

## Đánh giá chất lượng trước khi dùng thật

- Bộ phiếu thử phải có người rà chuyên môn; đo chính xác OCR giá trị/đơn vị, đúng đối chiếu, nguồn hỗ trợ từng câu, mức hiểu của người dùng và tỷ lệ câu trả lời cần bác sĩ sửa.
- Tính năng chỉ được giới thiệu là hỗ trợ giáo dục/chuẩn bị khám cho đến khi có bác sĩ thẩm định và quy trình xác nhận phù hợp.
