# Thiết kế: Độ tin cậy, đo lường và trách nhiệm cho CBC Care Companion

## Mục đích

Giúp người dùng hiểu điều gì đã được kiểm tra, điều gì chưa được kiểm chứng, cách xử lý khi nghi kết quả sai và đội phát triển có thể đo chất lượng từng phần mà không quảng cáo nhầm một tỷ lệ benchmark nhỏ thành “độ chính xác y khoa”.

## Hiện trạng

- So sánh CBC là logic số học xác định; OCR ảnh là bản nháp AI cần người dùng kiểm tra và xác nhận.
- Chat LLM chủ yếu phân loại câu hỏi; câu trả lời dùng nội dung có kiểm soát. Vì vậy không có một con số duy nhất đại diện cho “AI chính xác”.
- Hồ sơ hiện có 24 ca tổng hợp. Báo cáo lịch sử ghi Qwen3:4b đạt 19/24 (79%) trên lượt 1; 5 lỗi, và chưa có lượt 2 trên code hiện tại. 5/5 ca được hai thành viên chấm thử có đồng thuận, nhưng đó không phải thẩm định lâm sàng.
- Chưa có benchmark OCR được chấm trên phiếu thật ẩn danh, cũng chưa có tập giải thích được bác sĩ thẩm định độc lập.

## Các hướng

1. **Chỉ thêm cảnh báo miễn trừ:** nhanh nhưng không phát hiện lỗi, không đo được chất lượng và dễ khiến người dùng tưởng phần mềm đã được kiểm chứng.
2. **Công bố một tỷ lệ chính xác chung:** dễ hiểu nhưng sai phương pháp vì trộn OCR, phép đối chiếu và diễn giải; dữ liệu hiện tại là ca tổng hợp, nhỏ và cũ.
3. **Tách từng lớp chất lượng và có cổng phát hành (chọn):** báo tỷ lệ đạt trên bộ ca cố định, đo OCR theo từng trường, đo logic đối chiếu bằng đáp án chuẩn, và chỉ đánh giá diễn giải lâm sàng bằng người chấm đủ chuyên môn. Không có số thì ghi “chưa đo”. Đây là cách phù hợp với dữ liệu và kiến trúc hiện có.

## Phạm vi

- Thêm công cụ offline tạo báo cáo từ CSV lượt chạy hiện có, gồm mẫu số, ca chưa chấm, lỗi kỹ thuật, tỷ lệ đạt chung và theo nhóm đã ánh xạ. Nhãn báo cáo phải nói đây là tỷ lệ đạt trên bộ ca cố định, không phải độ chính xác lâm sàng; không tạo khoảng tin cậy giả cho benchmark chủ đích.
- Thêm manifest nhóm metric, giữ nguyên `eval/benchmark.csv`, các output lịch sử và ngưỡng đã khóa. Không viết lại điểm run cũ.
- Thêm mẫu chấm mù độc lập cho diễn giải: độ đúng dữ kiện, hỗ trợ bởi nguồn, an toàn phạm vi, lỗi nghiêm trọng; lưu mã ca/phiên bản/chấm, không đưa thông tin nhận dạng bệnh nhân vào repo.
- Thêm một khu vực giải thích trong UI về AI/OCR/đối chiếu, trạng thái kiểm chứng thật hiện có, hướng xử lý khi thấy sai và cảnh báo không nhập thông tin nhận dạng khi gửi phản hồi.
- Viết quy trình trách nhiệm theo vai trò nội bộ: đội phát triển, đơn vị vận hành, bác sĩ đánh giá và người dùng. Đây là nguyên tắc quản trị sản phẩm, không phải kết luận pháp lý về bồi thường.

## Ngoài phạm vi

- Không tuyên bố độ chính xác lâm sàng, không tự sinh confidence score, chẩn đoán, mức độ khẩn cấp hay đề xuất điều trị.
- Không thu thập phiếu bệnh nhân hoặc gửi lỗi ra ngoài; không tạo kênh tiếp nhận giả khi chưa có người phụ trách.
- Không tự kết luận sản phẩm là/không là thiết bị y tế, hoặc chỉ định một cá nhân/pháp nhân chắc chắn chịu trách nhiệm pháp lý.
- Không đưa dữ liệu tổng hợp vào kiểm chứng lâm sàng và không sửa benchmark/điểm lịch sử để khớp phiên bản mới.

## Cổng chất lượng trước khi giới thiệu như sản phẩm dùng cho sức khỏe

1. Đối chiếu số học: 100% ca chuẩn, biên, chuyển đổi đơn vị và dừng khi thiếu/sai dữ kiện trong bộ kiểm thử đã duyệt.
2. OCR: báo exact match riêng cho mã chỉ số, giá trị, đơn vị, khoảng dưới/trên; dữ liệu OCR vẫn là nháp, người dùng phải xác nhận từng trường trước khi dùng.
3. Diễn giải: tập giữ lại độc lập, ít nhất hai người chấm độc lập trong đó có bác sĩ sản/phụ khoa hoặc huyết học; báo tỷ lệ đạt, lỗi nghiêm trọng, đồng thuận và bất đồng theo nhóm chỉ số. Bác sĩ chuyên môn phải chốt ngưỡng trước khi chấm.
4. Trải nghiệm: thử nghiệm tác vụ có quan sát; đo tỷ lệ người hiểu đúng “trong/thấp/cao theo khoảng” và hoàn thành sửa/xác nhận, không dùng mức hài lòng làm bằng chứng an toàn.
5. Quản trị: lưu commit, model/provider, prompt/source version, ngày chạy, người chấm và lỗi; rà phân loại pháp lý, quyền riêng tư và quy trình xử lý sự cố trước phát hành thật.

## Trách nhiệm

Không đẩy rủi ro sang mẹ bầu bằng một dòng “chỉ tham khảo”. Đội phát triển chịu trách nhiệm quản lý thay đổi, nguồn và kiểm thử; đơn vị vận hành chịu trách nhiệm cấu hình, bảo mật, giám sát và ứng phó sự cố; bác sĩ giữ quyền quyết định lâm sàng khi tham gia chăm sóc. Phân bổ trách nhiệm pháp lý thực tế phụ thuộc vai trò, mục đích sử dụng, cách quảng bá, triển khai và sự kiện cụ thể, cần chuyên gia pháp lý/y tế tại Việt Nam rà soát.
