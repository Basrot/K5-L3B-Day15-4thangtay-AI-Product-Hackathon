# Thiết kế: Cảnh báo nhóm chỉ số CBC và câu hỏi cho bác sĩ

## Mục đích

Giúp người dùng nhìn thấy ngay các chỉ số nằm ngoài khoảng đối chiếu, hiểu đó là tín hiệu cần xem cùng nhau chứ không phải chẩn đoán, và có bản tóm tắt/câu hỏi dễ mang tới buổi khám. Sửa nút “Soạn câu hỏi cho bác sĩ” để thao tác tạo nội dung ngay cạnh cảnh báo.

## Phương án và lựa chọn

1. Để LLM tự sinh chẩn đoán từ nhiều chỉ số: linh hoạt nhưng không phù hợp với bản demo y tế vì câu trả lời có thể tự tin quá mức hoặc bịa nguyên nhân.
2. Hiển thị cảnh báo dựa trên kết quả đã xác nhận, dùng nhóm câu giải thích có kiểm soát; LLM chỉ phân luồng câu hỏi theo thiết kế đã duyệt trước đó. **Chọn cách này** để AI vẫn hỗ trợ câu hỏi nhóm chỉ số nhưng các số và câu cảnh báo lâm sàng không do model tự tính/suy đoán.
3. Chỉ giữ bảng so sánh hiện tại và đổi nhãn nút: ít thay đổi nhưng không làm nút rõ ràng hơn và không giúp đọc nhóm kết quả.

## Hành vi

- Khi có từ hai dòng thấp/cao hơn khoảng, hiện thẻ “Nhóm chỉ số cần trao đổi” ở đầu kết quả; liệt kê mã, tên, giá trị, đơn vị và hướng lệch theo đúng phân tích đã xác nhận.
- Thẻ giải thích nhóm hồng cầu, bạch cầu và tiểu cầu bằng ngôn ngữ mô tả, nêu giới hạn của CBC, và đưa ra câu hỏi cụ thể để hỏi bác sĩ. Không kết luận bệnh, mức độ nguy hiểm, hay đề xuất tự điều trị.
- Nút “Soạn câu hỏi cho bác sĩ” hiện bản nháp ngay trong thẻ cảnh báo và đưa tiêu điểm/cuộn tới nội dung mới tạo.
- Nút hỏi AI về nhóm chỉ số gửi câu hỏi có bối cảnh chỉ từ phiếu đã xác nhận; không gửi dữ liệu OCR chưa được xác nhận.
- Lưu bản tóm tắt trong kết quả tải xuống để người dùng có thể mang tới buổi khám.

## Giới hạn và nguồn

- Giữ nguyên cách tính, đơn vị, khoảng tham chiếu, API sở hữu phiên và đăng nhập.
- Ngoài khoảng tham chiếu chỉ là vị trí tương đối, không phải chẩn đoán. CBC cần được diễn giải cùng triệu chứng, bệnh sử và xét nghiệm khác.
- Nguồn tham khảo cho nội dung: nghiên cứu CBC thai kỳ Việt Nam Pham et al. (2023); ACOG về xét nghiệm trong thai kỳ; MedlinePlus CBC và RBC indices; NHLBI về xét nghiệm xác định thiếu sắt. Nguồn không được dùng để suy ra bệnh cho một cá nhân.

## Tiêu chí hoàn thành

- Bấm nút soạn câu hỏi sẽ thấy câu hỏi ngay cạnh thẻ cảnh báo mà không phải tìm ở dưới phần so sánh.
- Phiếu có nhiều dòng lệch khoảng sẽ có tóm tắt rõ ràng, dựa trên đúng hàng đã xác nhận.
- Câu chữ phân biệt rõ trạng thái đối chiếu với chẩn đoán và hướng người dùng tới bác sĩ.
