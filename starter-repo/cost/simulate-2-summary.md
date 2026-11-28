# Tóm tắt mô phỏng simulate-2@20261128-094041

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| tra_cuu_mot_lan | 26 | 1 | 212 | 13 | 0.7 | 1.0 |
| theo_doi_tai_kham | 19 | 1 | 162 | 10 | 0.5 | 1.0 |
| hoi_nhieu_chi_so | 5 | 2 | 186 | 11 | 0.6 | 2.0 |

Tỉ lệ đạt dùng để tính: 22/24 (92%) — lượt run-2@20261128-093648

- Tỉ lệ đạt lấy từ lượt nhóm chọn: eval/run-2.csv (--rate-from).

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (100 người) | Chi phí / tháng — cơ sở (500 người) | Chi phí / tháng — cao (1.500 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gemini-3.1-flash-lite (vào 0.25 · ra 1.5 $/1M) | $0.000065 | $0.000071 | $0.000065 | $0.0114 | $0.0568 | $0.1705 | $0.00011 |
| gemini-4-hydrogen (vào 1.5 · ra 7.5 $/1M) | $0.00037 | $0.00041 | $0.00037 | $0.0651 | $0.3256 | $0.9767 | $0.00065 |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (1.1) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: qwen3:4b. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 0/50.
