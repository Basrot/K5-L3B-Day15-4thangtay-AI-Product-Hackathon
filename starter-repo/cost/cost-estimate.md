# Chi phí khi dùng thật

> Kết quả mô phỏng N3. Đây là ước tính token cho luồng đã xác nhận CBC, không phải báo giá triển khai đầy đủ.

## 1. Đầu vào

- **Persona** (`cost/personas.yaml`): 3 kiểu, tỷ lệ 50% / 35% / 15%; tương ứng 1 / 2 / 4 phiên mỗi người mỗi tháng và 1 / 1 / 2 lượt hỏi mỗi phiên. Tất cả là **tự ước tính**, chưa được kiểm chứng qua phỏng vấn.
- **Số người dùng**: thấp 100 · cơ sở 500 · cao 1.500 mỗi tháng. Nguồn: tự ước tính quy mô triển khai beta (chiếm `< 1.5%` quy mô tự ước tính `~100.000` thai phụ tự xem phiếu/tháng ở `spec.md §2`; riêng một bệnh viện sản tuyến cuối là BV Từ Dũ đã có `~1.000.000` lượt khám và `>60.000` ca sinh/năm), không phải số người dùng đang dùng sản phẩm thật.
- **Giá model trả phí** (USD/1 triệu token; truy cập 27/11/2026): [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing) — Gemini 3.1 Flash-Lite, input $0.25 / output $1.50; Gemini 4 Hydrogen, input $1.50 / output $7.50. Giá là cấu hình standard paid tier trong `cost/personas.yaml`; kiểm tra giá và khả năng truy cập model trước khi triển khai.
- **Tỷ lệ đạt dùng để tính**: 19/24 (79%) — `run-1@20261127-163814`. Chưa có run 2; do đó đây là ước tính tạm, không phải tỷ lệ sau cải tiến.
- Token đo trên **qwen3:4b** local, tính theo giá **Gemini 3.1 Flash-Lite** và **Gemini 4 Hydrogen**. Tokenizer, giá thực tế, retry và chính sách cache có thể làm chi phí thực khác.

## 2. Kết quả mô phỏng

Lệnh `python run.py simulate --rate-from eval/run-1.csv` · `cost/simulate-1.csv` · run `simulate-1@20261127-164346` · 50 phiên · seed 42. Lỗi mô phỏng: 0/50.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| `tra_cuu_mot_lan` | 26 | 1 | 263 | 17 | 0.9 | 1.0 |
| `theo_doi_tai_kham` | 19 | 1 | 226 | 15 | 0.8 | 1.0 |
| `hoi_nhieu_chi_so` | 5 | 2 | 460 | 30 | 1.6 | 2.0 |

| Model (giá input/output USD / 1M token) | Chi phí / phiên | Chi phí / task thành công | / tháng — thấp (100 người) | / tháng — cơ sở (500 người) | / tháng — cao (1.500 người) | / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|
| Gemini 3.1 Flash-Lite ($0.25 / $1.50) | $0.000094 | $0.00012 | $0.0197 | $0.0984 | $0.2953 | $0.00020 |
| Gemini 4 Hydrogen ($1.50 / $7.50) | $0.00054 | $0.00068 | $0.1126 | $0.5628 | $1.69 | $0.0011 |

Chi phí/task thành công = chi phí trung bình mỗi phiên ÷ tỷ lệ đạt 19/24. Số mô phỏng được sinh từ phân bố persona đã cấu hình; bảng gốc và công thức chi phí nằm trong `cost/simulate-1-summary.md`. Phạm vi không bao gồm OCR/ảnh, hosting, lưu trữ, kiểm duyệt của nhân viên y tế hay thời gian chạy Zipformer.

## 3. So với impact

- Impact/người/tháng (`spec.md` §2): Ước tính sơ bộ ở `spec.md §2` là **`22.5` phút/người/tháng** *(tự ước tính dựa trên `1.5` lần/tháng × `15` phút/lần; chưa đo trực tiếp từ phỏng vấn `P1–P3`)*.
- Chi phí/người/tháng (kịch bản cơ sở từ `simulate-1`, tỷ lệ đạt `19/24 = 79%`): khoảng **`$0.00020`** với mức giá Gemini 3.1 Flash-Lite; khoảng **`$0.0011`** với Gemini 4 Hydrogen (`$0.00012–$0.00068`/task thành công).
- **Kết luận:** Nếu giả định `22.5` phút/người/tháng *(tự ước tính)* giữ vững trong thực tế, chi phí token LLM rất nhỏ so với thời gian tra cứu và lo lắng tiết kiệm được; tuy nhiên **chưa chốt hiệu quả cuối cùng** cho tới khi xác thực tần suất & số phút thật qua phỏng vấn/thử nghiệm người dùng, tính thêm chi phí OCR/hosting và có kết quả lượt đánh giá 2 (`eval/run-2.csv`).

## 4. Giới hạn và bước tiếp theo

- Chạy lại mô phỏng sau lượt đánh giá 2 bằng `python run.py simulate --rate-from eval/run-2.csv`.
- Thêm chi phí OCR theo tỷ lệ sử dụng ảnh và giá dịch vụ; đo riêng thời gian/chí phí vận hành Zipformer local khi có usage log.
- Thay ước tính persona và quy mô người dùng bằng số liệu phỏng vấn/khảo sát; xác nhận lại giá model trước triển khai.
