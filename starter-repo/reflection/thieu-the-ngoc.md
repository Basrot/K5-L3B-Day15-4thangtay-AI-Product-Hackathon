# Reflection — Thiều Thế Ngọc

1. Vai trò của em là **N3 — Evaluation & Cost**. Em tham gia xây bộ benchmark 24 câu và 3 metric, chấm chéo 5 câu với N1, rồi chạy/chấm lượt 2 trên cùng bộ câu. Kết quả và cách chấm được ghi ở `eval/run-2.csv`, `eval/report.md` và `eval/README.md`. Em cũng chạy mô phỏng 50 phiên và cập nhật chi phí ở `cost/`.

2. Em dùng Codex để hỗ trợ chạy lệnh đánh giá và mô phỏng, kiểm tra tính nhất quán của các file kết quả, và soạn phần báo cáo. Em tự đối chiếu điểm từng câu với `pass_criterion`; ví dụ, không đổi điểm B21 chỉ để khớp câu trả lời của model, mà ghi rõ vì sao input và expected chưa thống nhất.

3. B21 trượt vì câu thử thiếu `reference_mode: lab`, trong khi đáp án kỳ vọng hệ thống không dùng khoảng nghiên cứu thay cho khoảng lab bị thiếu. Em học được rằng benchmark phải nêu rõ chế độ tham chiếu cần kiểm tra để kết quả chấm có thể lặp lại. Khi phát hiện fixture mơ hồ, cần báo cáo giới hạn và giữ nguyên kết quả đã chấm, không sửa dữ liệu sau khi chạy.
