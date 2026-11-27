# Thiết kế: Luồng đọc phiếu CBC dễ hiểu cho mẹ bầu

## Mục đích

Giúp mẹ bầu biết bắt đầu ở đâu, nhập hoặc đọc ảnh phiếu, kiểm tra dữ liệu, rồi hiểu con số đang ở đâu so với khoảng được chọn và chuẩn bị câu hỏi cho bác sĩ. Màn hình cần ưu tiên phần hữu ích nhất và để chi tiết tham khảo mở khi người dùng cần.

## Những vấn đề thấy trong giao diện hiện tại

- Trước khi có kết quả, biểu mẫu và một thẻ kết quả trống nằm cạnh nhau trên màn hình rộng.
- Sau khi xác nhận, biểu mẫu vẫn chiếm phần lớn màn hình dù người dùng thường muốn xem kết quả trước.
- Danh sách tám chỉ số có vùng cuộn riêng, gây thêm một vùng cuộn lồng trên điện thoại.
- Phần chọn khoảng nghiên cứu giải thích dài trước khi người dùng bắt đầu nhập.
- Câu hỏi gợi ý đang cố định HGB/WBC dù phiếu có thể không có các dòng đó hoặc HGB không thấp.
- Bảng, lịch sử, so sánh và hỏi đáp xuất hiện liên tiếp khiến người dùng khó biết nên nhìn phần nào trước.

## Các phương án đã cân nhắc

1. **Giữ dashboard hai cột và chỉ rút gọn nội dung.** Ít thay đổi cấu trúc, nhưng vẫn để biểu mẫu và kết quả cạnh tranh sự chú ý, đặc biệt khi phiếu chưa được xác nhận.
2. **Luồng tập trung theo trạng thái phiếu (chọn).** Khi chưa xác nhận, chỉ ưu tiên biểu mẫu. Sau khi xác nhận, thu biểu mẫu lại và đưa tóm tắt, các dòng cần xem, cùng câu hỏi phù hợp với phiếu lên trước; cho mở lại biểu mẫu để chỉnh. Giữ bảng đầy đủ, nguồn nghiên cứu, so sánh lịch sử ở các phần tiếp theo. Cách này giữ nguyên phép tính/API và giảm thay đổi rủi ro.
3. **Wizard nhiều trang với từng bước riêng.** Hướng dẫn rất chặt nhưng đòi hỏi chuyển trang, quản lý trạng thái nhiều hơn và làm thao tác sửa phiếu cũ kém trực tiếp; chưa phù hợp với bản demo hiện tại.

## Hành vi giao diện

- Phần đầu màn hình nói rõ mục tiêu bằng câu ngắn: nhập hoặc chụp phiếu, kiểm tra thông tin, xem kết quả và chuẩn bị câu hỏi.
- Trạng thái quy trình cho biết người dùng đang thêm phiếu, kiểm tra dữ liệu hay xem kết quả.
- Khi chưa có kết quả, biểu mẫu chiếm chiều rộng chính; không hiện thẻ kết quả trống cạnh bên.
- Hướng dẫn về các giai đoạn thai kỳ và nguồn khoảng được thu vào phần giải thích mở rộng. Người dùng vẫn thấy tên lựa chọn bằng ngôn ngữ đời thường.
- Các trường nhập có nhãn gắn với từng chỉ số; danh sách chỉ số cuộn theo trang, không cuộn lồng.
- Sau xác nhận, biểu mẫu thu lại mặc định và có nút mở để sửa. Phần kết quả hiển thị ngay sau đầu trang.
- Chỉ thu biểu mẫu khi đã có kết quả phân tích hợp lệ. Nếu xác nhận lỗi hoặc phiếu cũ chưa thể tải phân tích, biểu mẫu vẫn mở để người dùng sửa hoặc bổ sung.
- Tóm tắt nêu rõ số dòng thấp hơn, nằm trong hoặc cao hơn khoảng; giải thích đó chỉ là vị trí của con số so với khoảng đang dùng.
- Hỏi đáp dùng câu gợi ý tạo từ các chỉ số thực sự có trong phiếu đã xác nhận. Nếu phiếu không có chỉ số cần hỏi, giao diện không gợi ý chỉ số đó.
- Chi tiết toàn bộ chỉ số, nguồn tham khảo, so sánh theo lần xét nghiệm và lịch sử vẫn truy cập được nhưng có thứ bậc rõ hơn phần tóm tắt.
- Trên màn hình nhỏ, các vùng xếp thành một cột, điều khiển dễ chạm, nội dung không bị giới hạn bởi vùng cuộn bên trong.
- Tiến trình phải có nhãn chữ và trạng thái hiện tại cho công nghệ hỗ trợ; không chỉ dựa vào màu. Nút mở sửa phải có tên rõ và giữ ngữ cảnh cuộn hợp lý.

## Giới hạn

- Không thay đổi số liệu, khoảng tham chiếu, phân loại trạng thái, lưu trữ, quyền riêng tư hoặc API.
- Không để AI tính toán, đánh giá bệnh hay đưa khuyến nghị điều trị. Câu trả lời về trạng thái lấy từ kết quả đối chiếu đã xác nhận; các giới hạn lâm sàng vẫn được nói rõ.
- Không ẩn chức năng chỉnh phiếu, xem nguồn hoặc xóa/mở lịch sử.

## Tiêu chí hoàn thành

- Người mới đăng nhập nhìn thấy một hành động bắt đầu chính và hiểu cần nhập/chụp phiếu rồi xác nhận.
- Sau xác nhận, người dùng thấy tóm tắt và đường dẫn đến câu hỏi liên quan mà không phải rà qua bảng dài.
- Câu hỏi gợi ý chỉ nhắc chỉ số có trong phiếu và khớp với trạng thái của dòng.
- Mọi thông tin chi tiết hiện có vẫn có thể mở lại; màn hình nhỏ không cần cuộn bên trong danh sách chỉ số.
- Câu chữ không gọi trạng thái trong khoảng là bình thường hay xem đó là chẩn đoán.
