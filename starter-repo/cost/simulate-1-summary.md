# Tóm tắt mô phỏng simulate-1@20261127-164346

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| tra_cuu_mot_lan | 26 | 1 | 263 | 17 | 0.9 | 1.0 |
| theo_doi_tai_kham | 19 | 1 | 226 | 15 | 0.8 | 1.0 |
| hoi_nhieu_chi_so | 5 | 2 | 460 | 30 | 1.6 | 2.0 |

Tỉ lệ đạt dùng để tính: 19/24 (79%) — lượt run-1@20261127-163814

- Tỉ lệ đạt lấy từ lượt nhóm chọn: eval/run-1.csv (--rate-from).

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (100 người) | Chi phí / tháng — cơ sở (500 người) | Chi phí / tháng — cao (1.500 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gemini-3.1-flash-lite (vào 0.25 · ra 1.5 $/1M) | $0.000094 | $0.00012 | $0.00011 | $0.0197 | $0.0984 | $0.2953 | $0.00020 |
| gemini-4-hydrogen (vào 1.5 · ra 7.5 $/1M) | $0.00054 | $0.00068 | $0.00061 | $0.1126 | $0.5628 | $1.69 | $0.0011 |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (1.1) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: qwen3:4b. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 0/50.
