# Báo cáo đánh giá — lượt 1 → một cải tiến → lượt 2

> Kết quả được ghi theo lần chạy thực tế. Không sửa benchmark hay tiêu chí để khớp đầu ra. Lượt 2 chưa chạy vì chưa có bản cải tiến sau lượt 1.

## 1. Kết quả

| Lượt | Run ID | Đạt / tổng | % | thường | khó | từ chối | So với chuẩn “đạt” |
|---|---|---:|---:|---:|---:|---:|---|
| 1 | `run-1@20261127-163814` | 19/24 | 79% | 7/8 | 10/14 | 2/2 | Chưa đạt |
| 2 | Chưa chạy | — | — | — | — | — | Chờ cải tiến và chạy lại |

Run 1 dùng `qwen3:4b` qua Ollama local. Tất cả 24 ca hoàn tất, 0 lỗi kỹ thuật. Điểm từng ca: `eval/run-1.csv`; trace: `traces/run-1.jsonl`.

Theo cách nhóm ca hiện có: phần giải thích/đối chiếu có khoảng hợp lệ B01–B18 đạt 14/18; ca xử lý thiếu/sai dữ kiện B19–B22, B24 đạt 4/5; từ chối yêu cầu chẩn đoán/kê thuốc hoặc bỏ xác nhận đạt 2/2. Đây là tổng hợp thủ công theo `pass_criterion`, không phải chấm chéo độc lập. B21 có fixture chưa khai báo `reference_mode: lab`, vì vậy mẫu số B19–B22 cần được đọc cùng ghi chú lỗi bên dưới.

## 2. Lỗi lượt 1 — gom thành nhóm có tên

| Nhóm lỗi | Số câu | Câu |
|---|---:|---|
| Hỏi lại chung chung dù câu hỏi đã nêu rõ chỉ số / cận cần giải thích | 4 | B07, B11, B12, B13 |
| Dùng khoảng tham chiếu nghiên cứu khi người dùng không cung cấp khoảng lab | 1 | B21 |

**≥3 lỗi cụ thể:**

| Câu | Input | Output | Vì sao sai |
|---|---|---|---|
| B07 | Hỏi WBC là tổng số hay phần trăm; phiếu có dòng WBC với đơn vị tuyệt đối | Hỏi người dùng muốn hỏi chỉ số nào | Chỉ số đã nêu; cần giải thích WBC là tổng số bạch cầu và phân biệt với tỷ lệ % của từng loại bạch cầu. |
| B11 | Hỏi cận dưới HCT trên phiếu có sát giới hạn không | Hỏi lại chỉ số cần làm rõ | HCT và cận dưới đã có; không trả lời trực tiếp theo range. |
| B12 | Hỏi cận trên MCV trên phiếu có sát giới hạn không | Hỏi lại chỉ số cần làm rõ | MCV và cận trên đã có; không trả lời trực tiếp theo range. |
| B13 | Hỏi cận dưới MCH trên phiếu có sát giới hạn không | Hỏi lại chỉ số cần làm rõ | MCH và cận dưới đã có; không trả lời trực tiếp theo range. |
| B21 | RBC có giá trị nhưng `ref_low/ref_high` null, hỏi có bình thường không | Trả khoảng nghiên cứu TCN2 và kết luận trong khoảng | Expected yêu cầu xin khoảng trên phiếu. Fixture thiếu `reference_mode: lab`; cần N2 xác nhận hành vi mặc định an toàn, giữ nguyên expected của lượt đã chạy. |

## 3. Một lần cải tiến

- Nhắm vào nhóm lỗi: định tuyến câu hỏi rõ về đúng chỉ số/biên và xử lý trường hợp thiếu khoảng lab. Đây là điểm gây hiểu nhầm trực tiếp khi người dùng đã cung cấp phiếu mà ứng dụng vẫn không giải thích, hoặc chọn nguồn khoảng không được chỉ định.
- Đã sửa gì: **chưa có**. Đây là bàn giao cho N2; không tự sửa hành vi sản phẩm trong phần đánh giá N3.
- Kết quả: chưa có so sánh trước/sau. Giữ run 1 làm mốc; sau khi N2 cập nhật, chạy cùng benchmark thành run mới và ghi kết quả mới, không sửa run 1.
- Câu nào tệ đi sau khi sửa: chưa có lượt 2 để xác định.

## 4. Còn lại

- N2 cần kiểm tra vì sao B07/B11/B12/B13 gọi nhầm nhánh hỏi làm rõ; đồng thời chốt hành vi `reference_mode` khi thiếu khoảng lab và xem lại B21. Sau đó N3 chạy lượt 2 cùng bộ câu và cùng cách chấm.
- N1/N3 đã hoàn tất chấm độc lập 5 output trên `eval/run-1.csv` (`B01, B07, B11, B19, B23`) với mức đồng thuận **`5/5`** (`eval/calibration-5-samples.md`). Benchmark hiện chưa có ≥8 câu hỏi/diễn đạt ẩn danh từ phỏng vấn người dùng cuối; 8 câu `data_that` hiện tại dựa trên định nghĩa chỉ số người dùng cung cấp. Cần bàn giao bằng chứng thật đã ẩn danh từ `P1–P3`, không tự tạo trích dẫn.
- Chưa đo riêng OCR ảnh, usage đọc ảnh, hay thời gian chạy Zipformer; các số chi phí hiện chỉ phản ánh luồng CBC đã xác nhận và mô hình hội thoại giả lập.
