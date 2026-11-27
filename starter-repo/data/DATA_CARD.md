# Data card — dữ liệu bản chạy thử dùng

> Điền ở guide bước 2.4 (bản đầu ở CP2, đủ ở CP3). Ôn lại: ngày 6 · lab ngày 6. Chấm ở rubric R4.
> Một trang. Mỗi dataset một mục. Dữ liệu chạy thử (bài mẫu, thông báo mẫu, đoạn transcript…) để trong thư mục `data/` này.
> Không commit nguyên tài liệu khoá, dữ liệu cá nhân thật hay nguyên file data BTC cấp — chỉ đoạn trích ngắn, bản viết lại, hoặc số đã tổng hợp.

## Dataset 1 · Benchmark N3 8 chỉ số CBC

| | |
|---|---|
| Dùng để làm gì | Kiểm bộ câu hỏi/giải thích CBC và logic so sánh với khoảng in trên phiếu trong `eval/benchmark.csv`; không huấn luyện model |
| Từ đâu | 8 định nghĩa chỉ số do người dùng cung cấp; 16 tình huống do nhóm tự viết |
| Xử lý những bước gì | Không có bản ghi bệnh nhân; tạo payload JSON tổng hợp thủ công, không lọc hoặc làm sạch hồ sơ thực |
| Số dòng / số đoạn | 24 ca: thường 8, khó 14, từ chối 2 |
| Phiên bản / ngày lấy | Benchmark hiện tại trong repo, chạy ngày 27/11/2026 |
| Nhãn | `synthetic`; 8 định nghĩa thuộc nguồn nội dung người dùng cung cấp, không phải dữ liệu lâm sàng |
| Giới hạn | Giá trị và khoảng tham chiếu là fixture giả lập; không đại diện quần thể, phòng xét nghiệm, hay ngưỡng lâm sàng. Chưa có ≥8 câu hỏi ẩn danh từ phỏng vấn người dùng cuối. |

**Data `synthetic` (nhóm tự sinh):** ghi cách sinh (prompt / script), seed, người kiểm, số dòng đã kiểm tay. Data tự dựng **không phải bằng chứng pain**.

## Dataset 2 · Vietnam Pregnancy Reference Study (tài liệu tham khảo, chưa dùng chấm run 1)

| | |
|---|---|
| Dùng để làm gì | Tham khảo khoảng huyết học thai kỳ / thiết kế ca kiểm thử về sau; không dùng làm giá trị thay thế khoảng trên phiếu trong run 1 |
| Từ đâu | File Excel `Vietnam_Pregnancy_Reference_Study.xlsx` người dùng gửi kèm và mô tả đi cùng; bài báo DOI [10.1186/s12884-023-06106-2](https://doi.org/10.1186/s12884-023-06106-2) |
| Xử lý những bước gì | Chưa import/biến đổi trong run 1; không sao chép dữ liệu cá nhân vào repo |
| Số dòng / số đoạn | Theo mô tả người gửi: 867 bản ghi, giữ cả bản ghi lặp; tam cá nguyệt 1/2/3 lần lượt 305/276/286; 837 panel CBC và 836 panel đông máu đầy đủ |
| Phiên bản / ngày lấy | File đính kèm người dùng; bảng dữ liệu có tuổi thai dạng `21w3d` và cột tam cá nguyệt đã chốt, tuần 28 thuộc TCN2 |
| Nhãn | Dữ liệu nghiên cứu; mô tả số lượng được ghi nhận từ thông tin người gửi, chưa kiểm tra trực tiếp nội dung workbook trong lượt đánh giá này |
| Giới hạn | Nghiên cứu không thay thế khoảng tham chiếu trên phiếu của từng phòng xét nghiệm hoặc ngưỡng quyết định lâm sàng. Cần kiểm tra điều kiện áp dụng, đơn vị, quần thể và cách phân nhóm trước khi dùng làm nguồn so sánh. |
