# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code bản chạy thử | Codex / Antigravity | Hỗ trợ viết `tools.py`, `references.py`, `agent.py`, tích hợp ONNX STT/TTS và unit test | Kiểm tra quy đổi đơn vị `Decimal`, ranh giới tuần thai và chạy bộ `unittest` | Nguyễn Gia Nam (N2) |
| Prompt / thiết kế lời gọi mô hình | Codex / Antigravity | Nháp schema JSON phân loại `intent` + `analyte` và các câu định nghĩa ngắn | Rà không cho LLM tự tính số hay chẩn đoán/kê thuốc | Nguyễn Gia Nam (N2) |
| Đào data (viết script đếm, gợi ý nhãn) | Antigravity | Hỗ trợ viết script `openpyxl` đếm `N = 837` và script `evidence/mine_public_qa.py` quét đa nguồn (`300` trang `tudu.com.vn` + `53` trang Sản phụ khoa & `6` trang Huyết học `medlatec.vn`: `M = 4.166 → N = 124` bài) kèm tự động xóa `faq-item-author` & PII | Đối chiếu số *Pham et al. (2023)* (`416/837`, `95/837`), kiểm lọc thủ công loại các bài nhiễu (Rubella, β-hCG, 75g đường, nước tiểu, soi tươi, HIV/VGB), kiểm tra khớp 124 nhãn `TD01–TD85` & `ML01–ML39`, kiểm tra độ phủ 8 chỉ số (`59/62 = 95.16%`) và đối chiếu nguồn Bộ Y tế / Viện Dinh dưỡng / BV Từ Dũ | Đào Ngọc Hân (N1) |
| Rà câu hỏi phỏng vấn / khảo sát | Antigravity | Chỉ rà bỏ câu dẫn dắt và soạn khung ghi chép theo nguyên tắc Mom Test | Tự liên hệ, phỏng vấn thật và ghi chép nguyên văn (không dùng AI sinh lời người dùng) | Đào Ngọc Hân (N1) |
| Viết câu thử (benchmark) | Codex / Antigravity | Hỗ trợ chuẩn hóa định dạng JSON cho 24 câu `benchmark.csv` và 15 câu ứng viên `n1-candidate-cases.csv` | Gắn rõ `source`, đối chiếu nguồn `TD01/TD02/TD08/TD36/ML14`, kiểm tay điều kiện `pass_criterion` và biên số học từng câu | Thiều Thế Ngọc (N3) & Đào Ngọc Hân (N1) |
| Sinh data `synthetic` (nếu có) | Antigravity | Dựng HTML + kết xuất 3 ảnh phiếu giả lập `cbc-mock-01..03.png` kèm JSON | Kịch bản cố định tất định · kiểm tay 24/24 dòng khớp 100% PNG ↔ JSON | Đào Ngọc Hân (N1) |
| Chấm cột `pass` bằng LLM (nếu có) | Antigravity (hỗ trợ rà tiêu chí) | Hỗ trợ N1 chấm độc lập 5 mẫu trên `eval/run-1.csv` (`B01, B07, B11, B19, B23`) đối chiếu với N3 (`eval/calibration-5-samples.md`); lượt chính thức không dùng LLM chấm tự động | N1 rà kiểm từng lý do chấm theo `metric_spec.yaml` & `pass_criterion` và đối chiếu khớp `5/5` với N3; lượt chính thức N3 chấm tay 100% | Thiều Thế Ngọc (N3) & Đào Ngọc Hân (N1) |
| Slide, văn bản | Antigravity | Hỗ trợ định dạng bảng Markdown trong `spec.md`, `canvas.md`, `DATA_CARD.md` | Rà soát toàn bộ con số, nguồn trích dẫn và trình bày demo | Trần Trọng Đức Tài (N4) & cả nhóm |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).
