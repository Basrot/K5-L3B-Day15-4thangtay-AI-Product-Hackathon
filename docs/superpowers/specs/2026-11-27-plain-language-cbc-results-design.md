# Thiết kế: Giải thích CBC bằng ngôn ngữ dễ hiểu

## Mục tiêu

Giúp người dùng không có chuyên môn hiểu mốc tuần thai, trạng thái so sánh CBC và giới hạn của kết quả. Giữ nguyên dữ liệu và phép tính hiện có; không để chatbot tự tạo chẩn đoán hoặc hướng điều trị.

## Phương án

- **A — Mẫu câu có kiểm soát (đã chọn):** giải thích do code tạo từ kết quả tính được; LLM chỉ chọn ý định/câu hỏi và mã chỉ số. Câu trả lời nhất quán, dễ kiểm tra.
- **B — LLM tự viết toàn bộ:** linh hoạt hơn nhưng khó bảo đảm giữ nguyên số liệu và không diễn giải vượt phạm vi.

## Thiết kế

- Giải nghĩa “tam cá nguyệt” là giai đoạn thai kỳ và hiển thị tuần cụ thể: giai đoạn 1 `1w0d–13w6d`, giai đoạn 2 `14w0d–28w6d`, giai đoạn 3 từ `29w0d` theo cách phân nhóm đang dùng trong ứng dụng.
- Đổi trạng thái thành “Thấp hơn khoảng tham chiếu”, “Trong khoảng tham chiếu”, “Cao hơn khoảng tham chiếu”. Mỗi trạng thái có một câu nói rõ đây là so sánh với khoảng đang chọn; không tự xác định có bệnh hay không. Dùng kết quả để gợi ý câu hỏi đem trao đổi với bác sĩ.
- Câu AI xưng “em”, gọi người dùng là “anh/chị”; dùng câu ngắn, tự nhiên, giữ nguyên giá trị, đơn vị, tên và nguồn khoảng.
- Làm cảnh báo nổi bật rằng “trong khoảng nghiên cứu” không đồng nghĩa “không có bệnh”, đặc biệt không dùng cận HGB nghiên cứu làm kết luận thiếu máu.
- Giữ hành vi OCR là bản nháp cần người dùng đối chiếu với phiếu gốc. TTS đọc đúng nội dung giải thích đã hiển thị.

## Ngoài phạm vi

Không đổi dữ liệu mẫu, giá trị/khoảng tham chiếu, logic tính toán, model LLM, ngưỡng chẩn đoán, hoặc cung cấp khuyến nghị điều trị.

## Kiểm tra dự kiến

Rà soát tất cả chuỗi UI/AI liên quan, kiểm tra build nếu dependency frontend có sẵn, và xác nhận các trạng thái/câu trả lời đều giữ đúng số liệu cùng nguồn. Không đánh giá độ đúng y khoa bằng model.
