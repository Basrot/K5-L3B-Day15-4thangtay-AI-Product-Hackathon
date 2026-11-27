# Thiết kế: Hiển thị kết quả CBC theo mức cần chú ý

## Mục tiêu

Giúp người không có chuyên môn (1) hiểu ngắn gọn từng chỉ số CBC và (2) nhận ra dòng nào nên đem hỏi bác sĩ, đồng thời xem được nguồn tham khảo khi cần.

## Các cách đã cân nhắc

- **Tóm tắt trước (đã chọn):** nêu các chỉ số thấp hơn/cao hơn khoảng đang chọn trước; gom tất cả chỉ số vào mục xem đầy đủ. Cách này giảm tải lúc đầu nhưng vẫn giữ chi tiết.
- **Thẻ giải thích đủ 8 chỉ số:** hiện ngay tên, kết quả, trạng thái và câu giải thích cho từng chỉ số. Dễ tra từng mục nhưng trang vẫn dài và nhiều thông tin.

## Thiết kế

- Phần đầu kết quả có câu ngắn như “Có 2 chỉ số nằm ngoài khoảng đang chọn” hoặc “Cả 8 chỉ số đều nằm trong khoảng đang chọn”. Không gọi kết quả là bình thường/bất thường và không chẩn đoán.
- Nếu có chỉ số thấp/cao hơn khoảng, đưa các chỉ số đó lên khu vực “Nên hỏi bác sĩ”. Mỗi dòng có tên tiếng Việt, mã chỉ số, kết quả, trạng thái và một câu ngắn về điều chỉ số đo. Không suy diễn ý nghĩa y khoa từ riêng phép so sánh.
- Gom toàn bộ 8 chỉ số vào mục mở rộng “Xem và hiểu đủ 8 chỉ số”. Mỗi chỉ số có tên tiếng Việt, mã, một câu mô tả ngắn nó đo gì, kết quả, trạng thái và khoảng so sánh.
- Đưa giải thích dài về trạng thái, nguồn nghiên cứu và lưu ý HGB vào mục “Cách đọc kết quả và nguồn tham khảo” có thể mở khi cần.
- Nếu không có chỉ số ngoài khoảng, không tạo cảnh báo giả; hiển thị rõ rằng các giá trị đều nằm trong khoảng đang chọn, kèm câu “điều này không loại trừ bệnh”.
- Câu tóm tắt hướng dẫn người dùng dùng khu vực “Nên hỏi bác sĩ” để chuẩn bị câu hỏi cho buổi khám; không tự động gắn mức độ nguy hiểm.
- Giữ nguyên giá trị, đơn vị, khoảng tham chiếu, phép tính, chức năng tải kết quả, hỏi đáp và nội dung đọc thành tiếng. Không đổi logic phân loại.

## Ngoài phạm vi

Không đổi ngưỡng, cách tính, dữ liệu mẫu, nội dung tư vấn y khoa hoặc kiến trúc AI.
