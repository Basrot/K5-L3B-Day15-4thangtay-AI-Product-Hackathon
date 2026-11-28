# Báo cáo đánh giá — lượt 1 → một cải tiến → lượt 2

> Kết quả được ghi theo lần chạy thực tế. Không sửa benchmark hay tiêu chí để khớp đầu ra. Run 1 được giữ nguyên; run 2 chạy cùng 24 câu sau bản cập nhật N2 trên `main`.

## 1. Kết quả

| Lượt | Run ID | Đạt / tổng | % | thường | khó | từ chối | So với chuẩn “đạt” |
|---|---|---:|---:|---:|---:|---:|---|
| 1 | `run-1@20261127-163814` | 19/24 | 79% | 7/8 | 10/14 | 2/2 | Chưa đạt |
| 2 | `run-2@20261128-093648` | 22/24 | 92% | 7/8 | 13/14 | 2/2 | Đạt tỷ lệ tổng; chưa đạt điều kiện cứng cho mọi ca thiếu/sai ngữ cảnh |

Hai lượt đều dùng `qwen3:4b` qua Ollama local. Run 1 và run 2 đều hoàn tất 24/24 câu, không có lỗi kỹ thuật. Run ID, model và token từng câu nằm trong CSV; trace ở `traces/run-1.jsonl` và `traces/run-2.jsonl`.

Run 2 được chấm thủ công theo `pass_criterion`: 22/24 (92%), tăng 3 câu và 13 điểm phần trăm so với run 1. B07 và B11–B13 đã trả lời đúng thay vì hỏi lại chung chung. Hai câu trượt là B06 (chưa phân biệt MCHC với MCH) và B21 (dùng khoảng nghiên cứu thay cho yêu cầu thiếu khoảng lab). B21 thiếu `reference_mode: lab` trong fixture; vì không sửa benchmark đã khóa, vẫn giữ điểm 0 theo expected hiện tại và ghi rõ đây là đầu vào mơ hồ.

## 2. Lỗi lượt 1 — gom thành nhóm có tên

| Lượt | Nhóm lỗi | Số câu | Câu |
|---|---|---:|---|
| 1 | Hỏi lại chung chung dù câu hỏi đã nêu rõ chỉ số / cận cần giải thích | 4 | B07, B11, B12, B13 |
| 1–2 | Dùng khoảng tham chiếu nghiên cứu khi expected yêu cầu thiếu khoảng lab; fixture thiếu `reference_mode` | 1 | B21 |
| 2 | Trả lời MCHC nhưng chưa phân biệt với MCH như câu hỏi yêu cầu | 1 | B06 |

**≥3 lỗi cụ thể:**

| Câu | Input | Output | Vì sao sai |
|---|---|---|---|
| B07 | Run 1 hỏi WBC là tổng số hay phần trăm; phiếu có dòng WBC với đơn vị tuyệt đối | Run 2 giải thích WBC là số lượng bạch cầu và đối chiếu đúng khoảng | Lỗi định tuyến của run 1 đã được khắc phục trong bản N2 hiện tại. |
| B11–B13 | Run 1 hỏi ranh giới HCT/MCV/MCH; câu hỏi đã nêu chỉ số và biên | Run 2 trả lời giá trị bằng cận vẫn nằm trong khoảng, không gắn cờ thấp/cao | Lỗi định tuyến và xử lý biên đã được khắc phục trong run 2. |
| B06 | Hỏi MCHC khác MCH ở điểm nào | Chỉ giải thích MCHC, không nêu MCH hoặc đối chiếu lượng với nồng độ | Câu trả lời chưa đủ theo tiêu chí; cần bổ sung phân biệt rõ hai chỉ số trong lần cải tiến tiếp theo. |
| B21 | RBC có giá trị nhưng `ref_low/ref_high` null, hỏi có bình thường không | Trả khoảng nghiên cứu TCN2 và kết luận trong khoảng | Expected yêu cầu không tự thay khoảng lab. Fixture không khai báo `reference_mode: lab`, nên đầu vào mơ hồ; giữ nguyên case và điểm 0, không sửa benchmark để hợp thức hóa kết quả. |

## 3. Một lần cải tiến

- Nhắm vào nhóm lỗi: định tuyến câu hỏi đã nêu chỉ số/biên và trả lời theo dữ liệu so sánh đã xác nhận.
- Bản N2 trên `main` đã ưu tiên trả lời tất định cho câu hỏi rõ về một chỉ số và trạng thái khoảng; phần chọn intent còn lại vẫn dùng model.
- Kết quả: run 1 `19/24 (79%)` → run 2 `22/24 (92%)`, cùng benchmark và cùng `qwen3:4b`. B07, B11–B13 được cải thiện; B06 và B21 còn trượt.
- B06 cần được sửa trong code của N2 bằng cách nêu rõ MCHC là nồng độ còn MCH là lượng hemoglobin trung bình mỗi hồng cầu. Đây là việc kỹ thuật ngoài phạm vi N3; run 2 tiếp tục được giữ nguyên và chưa có lượt full benchmark sau sửa.
- Không sửa `run-1.csv`, benchmark, expected hoặc ngưỡng đạt. B21 giữ nguyên điểm 0 và ghi chú vấn đề fixture.

## 4. Còn lại

- B21 cần được giữ như giới hạn của benchmark hiện tại; câu kiểm thử thiếu khoảng lab trong bộ tiếp theo phải chỉ rõ `reference_mode: lab`. Khi N2 có bản sửa B06, chạy lượt mới và giữ nguyên run 2; không ghi đè kết quả đã ghi.
- N1/N3 đã hoàn tất chấm độc lập 5 output trên `eval/run-1.csv` (`B01, B07, B11, B19, B23`) với mức đồng thuận **`5/5`** (`eval/calibration-5-samples.md`). Benchmark hiện chưa có ≥8 câu hỏi/diễn đạt ẩn danh từ phỏng vấn người dùng cuối; 8 câu `data_that` hiện tại dựa trên định nghĩa chỉ số người dùng cung cấp. Cần bàn giao bằng chứng thật đã ẩn danh từ `P1–P3`, không tự tạo trích dẫn.
- Chưa đo riêng OCR ảnh, usage đọc ảnh, hay thời gian chạy Zipformer; mô phỏng chi phí hiện hành cần chạy lại theo tỷ lệ đạt run 2 trước khi chốt CP4.
