# Độ tin cậy và xử lý khi kết quả có thể sai

## Phạm vi của ứng dụng

Ứng dụng là nguyên mẫu hỗ trợ đọc và chuẩn bị trao đổi về CBC thai kỳ. Nó không thay bác sĩ, không chẩn đoán, không kê thuốc và chưa được thẩm định để dùng làm căn cứ chăm sóc lâm sàng.

| Bước | Thành phần đang làm | Chất lượng đã biết |
|---|---|---|
| Đọc ảnh phiếu | Model thị giác tạo bản nháp các giá trị/đơn vị/khoảng | Chưa có kết quả exact-match trên tập ảnh được chấm; bắt buộc người dùng so lại từng ô với phiếu gốc. |
| So sánh với khoảng | Code chuẩn hóa đơn vị và so số đã xác nhận với khoảng đã chọn | Có benchmark tổng hợp lịch sử, nhưng cần chạy lại trên commit hiện tại và xác minh nguồn khoảng trước khi gọi là cổng phát hành. |
| Hỏi đáp | LLM nhận diện ý định/chỉ số; logic có kiểm soát tạo phần giải thích và dẫn nguồn | Chưa có đánh giá lâm sàng độc lập; không gọi tỷ lệ đạt benchmark là độ chính xác y khoa. |

## Số liệu hiện có — cần đọc đúng

Hồ sơ ghi một lượt lịch sử dùng **Qwen3:4b**, run `run-1@20261127-163814`: **19/24 ca tổng hợp đạt (79,2%)**, 5/24 không đạt, 0 lỗi kỹ thuật. Trong đó: giải thích 7/8; giá trị biên 5/8; đổi đơn vị 1/1; giải thích kết quả ngoài khoảng 1/1; dữ kiện thiếu/sai 3/4; nhánh từ chối/an toàn 2/2. Hai người chấm thử đồng thuận 5/5 ca được chọn, nhưng cả hai cùng chấm đạt 3/5.

Đây là tỷ lệ đạt trên 24 ca cố định, chủ đích và phần lớn tổng hợp; run có trước commit hiện tại. Nó **không** phải xác suất AI trả lời đúng cho một mẹ bầu, không chứng minh hiệu quả lâm sàng, và không cho biết độ chính xác OCR. Báo cáo mới tạo được bằng `node eval/quality-report.mjs eval/run-1.csv`. Chạy lại trên code hiện tại cần giữ benchmark và tiêu chí, ghi một run mới, rồi chấm từng output; không sửa điểm cũ.

## Bộ chỉ số cần theo dõi

1. **OCR exact match theo trường:** mã chỉ số, giá trị, đơn vị, cận dưới, cận trên. Báo `đúng / tổng có thể đọc` cho từng trường, số trường thiếu/không chắc, và tỷ lệ phiếu cần sửa. Không tính “được xác nhận” là “OCR đúng”; cần so với nhãn chuẩn được người kiểm tra độc lập chốt.
2. **Đối chiếu số học:** đúng trạng thái trên/dưới/trong khoảng, đúng quy đổi đơn vị, đúng xử lý hai cận bao gồm, và dừng với đơn vị/khoảng/giá trị thiếu hoặc không tương thích. Báo từng metric dưới dạng `đạt / tổng`, kèm lỗi còn lại.
3. **Giải thích:** người chấm đánh giá riêng tính đúng dữ kiện, câu có nguồn hỗ trợ, đúng phạm vi, và có lỗi an toàn nghiêm trọng hay không. Hai người chấm độc lập (trong đó có chuyên gia phù hợp), bất đồng chuyển người thứ ba phân xử. Báo tỷ lệ đồng thuận và lỗi theo HGB/RBC/HCT/MCV/MCH/MCHC/WBC/PLT, tam cá nguyệt, kiểu câu hỏi và mức chất lượng OCR.
4. **Khả năng hiểu và thao tác:** quan sát người dùng có phát hiện/sửa OCR sai, hiểu đúng nhãn tham chiếu, và biết cần hỏi bác sĩ điều gì. Báo số người/thành công trên tổng phiên; không suy ra an toàn từ lời khen hoặc mức hài lòng.

Không gộp bốn nhóm thành một “AI accuracy”. Tập tổng hợp chỉ kiểm tra logic và lỗi đã nghĩ tới; tập giữ lại phải tách theo **phiếu** (không chia ảnh/cùng người giữa train và holdout), ẩn danh hợp pháp và được người có chuyên môn kiểm nhãn. Bác sĩ chuyên môn và người phụ trách thống kê phải chốt cỡ mẫu/ngưỡng trước khi chấm; hiện chưa có đủ dữ liệu để đặt ra tỷ lệ lâm sàng.

`clinical-review-template.csv` chỉ lưu mã ca, phiên bản, mã vai trò người chấm và điểm rubric. Không ghi tên, ngày sinh, mã bệnh án, ảnh phiếu, giá trị CBC hay nội dung có thể nhận diện bệnh nhân vào repo. Chỉ dùng dữ liệu thật sau khi có cơ sở pháp lý, quy trình đồng thuận/ẩn danh, kiểm soát truy cập và thời hạn xóa phù hợp.

## Cổng phát hành đề xuất

- Tạm dừng phát hành nếu có lỗi nghiêm trọng: đảo trạng thái do đơn vị, dùng nhầm khoảng, chẩn đoán/điều trị vượt phạm vi, hoặc bỏ qua dữ liệu thiếu.
- Trước khi mở cho bệnh nhân dùng thật: rerun toàn bộ bộ ca trên commit chuẩn bị phát hành; đối chiếu source/reference version; kiểm thử OCR trên tập được người gán nhãn; có đánh giá diễn giải độc lập của bác sĩ và phân tích bất đồng.
- Sau phát hành: gắn phiên bản app/model/prompt/nguồn cho mỗi báo cáo đánh giá; có người nhận và phân loại sự cố; có thể tắt OCR/chat khi phát hiện lỗi; giữ nhật ký kỹ thuật tối thiểu, không lưu nội dung CBC trong log chỉ để tính điểm.
- Không bật hay quảng bá “mức tin cậy %” do LLM tự khai báo. Khi không đủ dữ kiện, phải dừng hoặc yêu cầu người dùng kiểm tra, không đoán.

## Khi người dùng nghi kết quả sai

1. Không dựa vào câu trả lời để tự chẩn đoán, đổi thuốc hoặc trì hoãn khám.
2. So lại ảnh/phiếu gốc, đặc biệt mã chỉ số, dấu thập phân, đơn vị, khoảng tham chiếu và tuổi thai; sửa bản nháp rồi chỉ xác nhận khi khớp.
3. Nếu con số hoặc lời giải thích vẫn không khớp, bỏ qua phần đó và hỏi bác sĩ/cơ sở xét nghiệm. Tình huống sức khỏe khẩn cấp cần liên hệ cơ sở y tế trực tiếp.
4. Khi báo lỗi cho nhóm phát triển, chỉ gửi mã ca/phiên bản và mô tả lỗi đã loại thông tin nhận dạng; không gửi ảnh hoặc dữ liệu sức khỏe qua kênh không được phê duyệt.

## Vai trò và trách nhiệm

Đây là nguyên tắc quản trị nội bộ, không phải kết luận phân bổ trách nhiệm theo luật:

- **Đội phát triển/chủ sản phẩm:** xác định mục đích sử dụng trung thực; kiểm chứng logic, nguồn và thay đổi; hiển thị giới hạn; bảo vệ dữ liệu; theo dõi và xử lý sự cố.
- **Đơn vị vận hành:** cấu hình đúng, cập nhật, kiểm soát truy cập, theo dõi lỗi và có cơ chế tắt/khôi phục.
- **Bác sĩ/cơ sở y tế (nếu dùng trong quy trình chăm sóc):** đánh giá kết quả trong bối cảnh lâm sàng và quyết định chuyên môn; không nên dựa duy nhất vào một bản tóm tắt chưa được xác nhận.
- **Người dùng:** kiểm tra dữ liệu OCR và không dùng nguyên mẫu như chẩn đoán. Đây không phải cách chuyển trách nhiệm của lỗi thiết kế/triển khai sang người bệnh.

Không thể chỉ từ code hay câu miễn trừ xác định ai sẽ chịu trách nhiệm pháp lý nếu xảy ra thiệt hại. Việc đó phụ thuộc mục đích, cách giới thiệu, tình huống sử dụng, vai trò của từng bên và luật áp dụng. Luật AI Việt Nam số 134/2025/QH15 có hiệu lực từ 01-03-2026; Luật Khám bệnh, chữa bệnh số 15/2023/QH15 có hiệu lực từ 01-01-2024. Việt Nam cũng có quy định quản lý trang thiết bị y tế và văn bản cập nhật gần đây; cần rà chức năng và mục đích dự kiến của chính sản phẩm, không suy ra phân loại chỉ từ disclaimer. Trước khi đưa sản phẩm ra dùng thật, cần luật sư và chuyên gia quản lý trang thiết bị y tế tại Việt Nam đánh giá phân loại, nghĩa vụ và quy trình. [Luật AI trên Cổng văn bản Chính phủ](https://vanban.chinhphu.vn/?docid=216334&pageid=27160&typegroupid=3) · [Luật Khám bệnh, chữa bệnh trên Cổng văn bản Chính phủ](https://vanban.chinhphu.vn/?classid=1&docid=207396&pageid=27160) · [Văn bản hợp nhất về quản lý trang thiết bị y tế](https://vanban.chinhphu.vn/?docid=217131&pageid=27160) · [Thông tư 24/2026/TT-BYT](https://vanban.chinhphu.vn/?docid=218703&pageid=27160).

Hướng dẫn FDA của Hoa Kỳ cũng cho thấy việc phân loại phần mềm phụ thuộc vào chức năng/mục đích cụ thể; guidance đó không thay thế tư vấn pháp lý Việt Nam. [FDA: Clinical Decision Support Software](https://www.fda.gov/medical-devices/digital-health-center-excellence/step-6-software-function-intended-provide-clinical-decision-support).
