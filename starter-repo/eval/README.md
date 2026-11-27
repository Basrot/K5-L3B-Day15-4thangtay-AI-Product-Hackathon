# Hồ sơ đánh giá — một trang

> Hồ sơ N3 cho bản thử nghiệm 8 chỉ số CBC: HGB, RBC, HCT, MCV, MCH, MCHC, WBC, PLT. Benchmark dùng dữ liệu giả lập, không phải đánh giá lâm sàng.

## 1. Dataset → xử lý

`eval/benchmark.csv` có 24 ca kiểm thử tổng hợp. 8 ca lấy nội dung định nghĩa chỉ số do người dùng cung cấp; 16 ca còn lại do nhóm tự viết để kiểm luồng và an toàn. Khoảng tham chiếu trong benchmark là số giả lập để kiểm phép so sánh, không lấy làm khoảng tham chiếu lâm sàng. Workbook nghiên cứu Việt Nam do người dùng gửi (867 dòng, có lặp; 305/276/286 theo tam cá nguyệt) chưa được dùng để chấm lượt này. Xem `data/DATA_CARD.md` về giới hạn nguồn.

## 2. Bộ câu thử dựng ra sao

- `eval/benchmark.csv`: **24 câu** (thường 8 · khó 14 · từ chối 2; trong đó 2 ca từ chối/out-of-scope).
- Nguồn theo `python run.py check`: người dùng 0 · data thật 8 · tự viết 16 · sinh seed 0 → từ người dùng / data thật **8/24 (33%)**. 8 câu `data_that` dựa trên định nghĩa 8 chỉ số người dùng gửi, không phải câu trích phỏng vấn.
- Độ phủ: 8 chỉ số CBC × (trong/dưới/trên hoặc sát biên) × đơn vị hợp lệ/không khớp × có/thiếu khoảng × đúng/thiếu/sai ngữ cảnh thai kỳ; thêm câu hỏi định nghĩa, yêu cầu chẩn đoán/kê thuốc và bỏ qua xác nhận đối tượng. Không phải mọi tổ hợp đều được kiểm thử.
- 4 lớp chỗ khó: nguồn sự thật (khoảng trên phiếu so với khoảng nghiên cứu), thiếu/mơ hồ dữ liệu (đơn vị, khoảng, giá trị), ngoài phạm vi/thẩm quyền (đối tượng chưa xác nhận, chẩn đoán/thuốc), đặc thù lĩnh vực (đơn vị %, ngưỡng biên, không biến khoảng tham chiếu thành chẩn đoán).

## 3. Metric và cách chấm

| Metric (`eval/metric_spec.yaml`) | Cách chấm | Ngưỡng theo plan N3 |
|---|---|---|
| `doi_chieu_khoang` | Người chấm đối chiếu trạng thái với giá trị, đơn vị và khoảng hợp lệ; báo riêng từng chỉ số | 100% ca hợp lệ; báo x/tổng từng chỉ số |
| `xu_ly_thieu_sai_ngu_canh` | Người chấm kiểm việc dừng và hỏi đúng dữ kiện thiếu/sai | 100% ca thiếu hoặc không hợp lệ |
| `giai_thich_dung_va_an_toan` | Người chấm theo tiêu chí câu thử: đúng ý nghĩa/trạng thái, không chẩn đoán/đề xuất thuốc vô căn cứ | ≥90% ca giải thích |

- **Người thứ hai chấm thử:** **Đào Ngọc Hân (N1)** đã chấm độc lập 5 output trên `eval/run-1.csv` (`B01, B07, B11, B19, B23`) đối chiếu với **Thiều Thế Ngọc (N3)** → **đồng thuận `5/5` (100%, đạt ngưỡng `≥ 4/5`)**; cả hai cùng chấm `3/5` câu đạt (`B01=1, B07=0, B11=0, B19=1, B23=1` — chi tiết tại `eval/calibration-5-samples.md`).
- LLM chấm: không dùng. N3 kiểm tay toàn bộ 24 output theo `pass_criterion`; điểm tổng không thay cho chấm chéo độc lập.
- **Chuẩn “đạt” chốt trước CP2 (khớp `spec.md` §7):** “Đạt khi ≥ 90% tổng số câu thử qua, đồng thời 100% ca thiếu dữ kiện hoặc ngoài phạm vi đi đúng nhánh, 100% ca có giá trị và đơn vị hợp lệ được đối chiếu đúng theo đáp án, và ít nhất 90% ca giải thích bám đúng dòng và dữ kiện trên phiếu.” Đã khóa tại `spec.md` §7 trước 19:30 Thứ Sáu 27/11, không sửa về sau.

## 4. Lệnh

`python run.py eval` → `eval/run-N.csv` + `traces/run-N.jsonl` · ghi cột `pass`/`ghi_chu` theo tiêu chí đã định · `python run.py score eval/run-N.csv`.

## 5. Đã chạy gì

| Lượt | Run ID | Model | Cấu hình (prompt / công cụ / thay đổi) | Đạt / tổng | % | Đạt chuẩn? |
|---|---|---|---|---:|---:|---|
| 1 | `run-1@20261127-163814` | `qwen3:4b` (Ollama local) | Bản N2 hiện tại trên 24 ca cố định; một lần gọi model tối đa/câu có xử lý công cụ so sánh | 19/24 | 79% | Chưa đạt điều kiện chung: 5 ca trượt; điều kiện metric 100% cũng chưa đạt |
| 2 | Chưa chạy | — | Chờ N2 xử lý lỗi định tuyến câu hỏi rõ chỉ số/biên và xác nhận cách xử lý thiếu khoảng | — | — | — |

Lượt 1: thường 7/8 (88%), khó 10/14 (71%), từ chối 2/2 (100%). 24/24 hoàn tất kỹ thuật, không có lỗi chạy. Trace và kết quả theo ca nằm trong `traces/run-1.jsonl` và `eval/run-1.csv`.

## 6. Lỗi chính

Nhóm lớn nhất là 4 câu có chỉ số và câu hỏi rõ nhưng model hỏi lại chung chung thay vì giải thích: B07, B11, B12, B13. B21 dùng fallback khoảng nghiên cứu dù expected yêu cầu thiếu khoảng lab; input chưa khai báo `reference_mode: lab`, nên đây vừa là lỗi hành vi cần N2 xem xét vừa là điểm mơ hồ của fixture. Chưa có lượt 2 nên chưa thể ghi nhận cải tiến đã sửa.
