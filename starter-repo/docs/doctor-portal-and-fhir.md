# Cổng bác sĩ và xuất FHIR

## Cổng bác sĩ

- Người đăng ký bác sĩ phải đăng nhập bằng Google để dùng email đã được Google xác minh, sau đó gửi họ tên, giấy phép hành nghề, chuyên khoa và nơi công tác.
- Admin kiểm tra giấy phép ngoài hệ thống rồi mới duyệt hồ sơ. Không duyệt chỉ dựa vào thông tin người đăng ký tự khai.
- Khi admin chấp thuận hoặc từ chối hồ sơ, số giấy phép đã nhập bị xóa khỏi hồ sơ ứng dụng; hệ thống chỉ giữ trạng thái, người duyệt và thời điểm quyết định.
- Mẹ bầu mở một phiếu đã xác nhận, nhập đúng email bác sĩ, xem nội dung đồng ý và chủ động cấp quyền. Quyền chỉ áp dụng cho phiếu đó, tự hết hạn sau 30 ngày và có thể thu hồi bất cứ lúc nào.
- Nếu phiếu bị sửa hoặc xác nhận lại, quyền chia sẻ cũ tự bị thu hồi; mẹ bầu cần cấp quyền lại cho phiên bản mới.
- Bác sĩ chỉ đọc phiếu được cấp quyền. Không truy cập được phiếu khác, lịch sử hỏi đáp hoặc bản nháp OCR. Mỗi lần mở phiếu được ghi nhật ký; mẹ bầu thấy thời điểm và số lượt xem.
- Admin có hàng đợi hồ sơ bác sĩ trong giao diện tài khoản admin. Việc bấm xác minh là quyết định của người quản trị, không phải xác minh tự động của AI.

## Xuất FHIR

Nút **Xuất FHIR** tải một Bundle JSON cho phiếu đã xác nhận, gồm Patient định danh giả danh trong file, DiagnosticReport và các Observation cho 8 chỉ số cốt lõi. Mã LOINC dùng cho các chỉ số: HGB `718-7`, RBC `789-8`, HCT `4544-3`, MCV `787-2`, MCH `785-6`, MCHC `786-4`, WBC `6690-2`, PLT `777-3`; mã đơn vị dùng UCUM. Mapping được đối chiếu với [LOINC CBC panel](https://loinc.org/58410-2/) và các mục thành phần được liên kết từ trang LOINC.

Bundle hiện không chứa danh tính thật, đơn vị xét nghiệm, thiết bị, người thực hiện hay chữ ký bác sĩ; các thông tin này không có trong dữ liệu ứng dụng. Đây là tệp trao đổi thử nghiệm, chưa được kiểm định với máy chủ FHIR của bệnh viện và không nên coi là hồ sơ bệnh án tích hợp hoàn chỉnh.

## Checklist kiểm tra thủ công trước demo

1. Tạo tài khoản bác sĩ bằng Google, gửi hồ sơ; xác nhận trạng thái chờ không mở được cổng.
2. Đăng nhập admin, kiểm tra giấy phép bên ngoài rồi duyệt hồ sơ.
3. Ở tài khoản mẹ bầu, xác nhận phiếu CBC, chia sẻ bằng đúng email bác sĩ và đồng ý; kiểm tra bác sĩ thấy đúng phiếu.
4. Thu hồi quyền ở tài khoản mẹ bầu; xác nhận bác sĩ không mở lại được phiếu. Kiểm tra lịch sử xem hiển thị đúng số lượt.
5. Tải FHIR từ phiếu đã xác nhận và xác nhận file không có tên/email thật; đối chiếu giá trị, đơn vị, khoảng tham chiếu và trạng thái với phiếu trên ứng dụng.

## Nhắc an toàn triệu chứng

Trang có danh sách nhắc một số dấu hiệu cảnh báo thai kỳ dựa trên [CDC Hear Her](https://www.cdc.gov/hearher/maternal-warning-signs/index.html). Đây là nhánh quy tắc cố định, không dùng LLM, không lưu lựa chọn và không gửi triệu chứng ra khỏi trình duyệt. Khi có dấu hiệu được chọn, ứng dụng hướng người dùng liên hệ ngay cơ sở sản khoa/cấp cứu tại nơi họ ở. Danh sách không đầy đủ và chưa được bác sĩ tại Việt Nam thẩm định; cần được bác sĩ sản khoa rà soát trước khi dùng trong chăm sóc thật.

## Chưa được khẳng định

- Chưa có xác minh giấy phép tự động; admin chịu trách nhiệm kiểm tra hồ sơ ngoài hệ thống.
- Chưa kiểm thử với máy chủ FHIR hoặc phần mềm bệnh viện.
- Nhắc an toàn triệu chứng chưa thay thế quy trình phân loại cấp cứu được cơ sở y tế phê duyệt.
- Ghi chú lâm sàng của bác sĩ, nhắn tin và thông báo đẩy chưa được triển khai.
- Giao diện hiện chỉ tiếng Việt; chưa có bản dịch tiếng Anh đã được người có chuyên môn rà soát.
- Đánh giá người dùng thật cần được nhóm thực hiện và ghi nhận trung thực; phần mềm không tự tạo kết quả phỏng vấn.
