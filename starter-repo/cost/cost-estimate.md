# Chi phí khi dùng thật

> Kết quả mô phỏng N3. Đây là ước tính token cho luồng đã xác nhận CBC, không phải báo giá triển khai đầy đủ.

## 1. Đầu vào

- **Persona** (`cost/personas.yaml`): 3 kiểu, tỷ lệ 50% / 35% / 15%; tương ứng 1 / 2 / 4 phiên mỗi người mỗi tháng và 1 / 1 / 2 lượt hỏi mỗi phiên. Tất cả là **tự ước tính**, chưa được kiểm chứng qua phỏng vấn.
- **Số người dùng**: thấp 100 · cơ sở 500 · cao 1.500 mỗi tháng. Nguồn: tự ước tính quy mô triển khai beta (chiếm `< 1.5%` quy mô tự ước tính `~100.000` thai phụ tự xem phiếu/tháng ở `spec.md §2`; riêng một bệnh viện sản tuyến cuối là BV Từ Dũ đã có `~1.000.000` lượt khám và `>60.000` ca sinh/năm), không phải số người dùng đang dùng sản phẩm thật.
- **Giá model trả phí** (USD/1 triệu token; truy cập 27/11/2026): [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing) — Gemini 3.1 Flash-Lite, input $0.25 / output $1.50; Gemini 4 Hydrogen, input $1.50 / output $7.50. Giá là cấu hình standard paid tier trong `cost/personas.yaml`; kiểm tra giá và khả năng truy cập model trước khi triển khai.
- **Tỷ lệ đạt dùng để tính**: 22/24 (92%) — `run-2@20261128-093648`. Đây là kết quả bộ kiểm thử N3, không phải tỷ lệ thành công lâm sàng.
- Token đo trên **qwen3:4b** local, tính theo giá **Gemini 3.1 Flash-Lite** và **Gemini 4 Hydrogen**. Tokenizer, giá thực tế, retry và chính sách cache có thể làm chi phí thực khác.

## 2. Kết quả mô phỏng

Lượt mô phỏng trước `simulate-1` được giữ nguyên. Kết quả hiện dùng cho CP4: `python run.py simulate --rate-from eval/run-2.csv` · `cost/simulate-2.csv` · run `simulate-2@20261128-094041` · 50 phiên · seed 42. Lỗi mô phỏng: 0/50.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| `tra_cuu_mot_lan` | 26 | 1 | 212 | 13 | 0.7 | 1.0 |
| `theo_doi_tai_kham` | 19 | 1 | 162 | 10 | 0.5 | 1.0 |
| `hoi_nhieu_chi_so` | 5 | 2 | 186 | 11 | 0.6 | 2.0 |

| Model (giá input/output USD / 1M token) | Chi phí / phiên | Chi phí / task thành công | / tháng — thấp (100 người) | / tháng — cơ sở (500 người) | / tháng — cao (1.500 người) | / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|
| Gemini 3.1 Flash-Lite ($0.25 / $1.50) | $0.000065 | $0.000071 | $0.0114 | $0.0568 | $0.1705 | $0.00011 |
| Gemini 4 Hydrogen ($1.50 / $7.50) | $0.00037 | $0.00041 | $0.0651 | $0.3256 | $0.9767 | $0.00065 |

Chi phí/task thành công = chi phí trung bình mỗi phiên ÷ tỷ lệ đạt 22/24. Số mô phỏng được sinh từ phân bố persona đã cấu hình; bảng run2 và công thức chi phí nằm trong `cost/simulate-2-summary.md`. Token được đo trên `qwen3:4b`, còn đơn giá tính theo các model Gemini trong bảng. Phạm vi không bao gồm OCR/ảnh, hosting, lưu trữ, kiểm duyệt của nhân viên y tế hay thời gian chạy Zipformer.

## 3. So với impact

- Impact/người/tháng (`spec.md` §2): Ước tính sơ bộ ở `spec.md §2` là **`22.5` phút/người/tháng** *(tự ước tính dựa trên `1.5` lần/tháng × `15` phút/lần; chưa đo trực tiếp từ phỏng vấn `P1–P3`)*.
- Chi phí/người/tháng (kịch bản cơ sở từ `simulate-2`, tỷ lệ đạt `22/24 = 92%`): khoảng **`$0.00011`** với mức giá Gemini 3.1 Flash-Lite; khoảng **`$0.00065`** với Gemini 4 Hydrogen (`$0.000071–$0.00041`/task thành công).
- **Kết luận:** Nếu giả định `22.5` phút/người/tháng *(tự ước tính)* giữ vững trong thực tế, chi phí token LLM thấp so với thời gian tra cứu ước tính. Đây vẫn là ước lượng mô hình, chưa gồm OCR/hosting và chưa được xác nhận bằng phỏng vấn. Run2 còn hai ca trượt (B06, B21), nên không diễn giải 92% thành độ tin cậy lâm sàng.

## 4. Giới hạn, độ nhạy sau nâng cấp hội thoại và bước tiếp theo

- **Phân tích độ nhạy khi bật chế độ hội thoại giải thích chi tiết (cập nhật sau CP4):** Ở bản nâng cấp trải nghiệm người dùng sau CP4 (`codebase/agent.py`), thay vì chỉ trả JSON định tuyến ngắn (`10–13` token ra ở `simulate-2`), model sinh trực tiếp đoạn giải thích tiếng Việt tự nhiên (`~80–220` từ, trung bình ước tính `~450` token vào / `~220` token ra; tối đa `1` lần gọi viết lại nếu hậu kiểm phát hiện chữ số tự sinh). Khi đó chi phí trung bình mỗi lượt hỏi ở mức giá **Gemini 3.1 Flash-Lite** tăng lên khoảng **`$0.00044`/lượt** (`~$0.0007–$0.0011`/người/tháng ở kịch bản cơ sở `500` người, tương đương **`~$0.35–$0.55`/tháng** toàn hệ thống) và ở mức **Gemini 4 Hydrogen** khoảng **`$0.0023`/lượt** (`~$1.90–$2.80`/tháng cho `500` người) — vẫn rất nhỏ so với thời gian tự tra cứu ước tính `22.5` phút/người/tháng.
- **Chi phí ngoài luồng chat văn bản:** Đọc phiếu từ ảnh JPG/PNG hoặc PDF tối đa 3 trang (`codebase/vision.py`) tốn thêm `1` lượt gọi model thị giác chỉ khi người dùng tải tệp lên; tổng hợp giọng nói `VieNeu TTS` chỉ phát sinh khi người dùng chủ động bấm *"Nghe đọc"*; còn nhận dạng giọng nói `Zipformer 150M INT8` chạy cục bộ trên CPU ONNX không tốn phí API ngoài.
- Thay ước tính persona và quy mô người dùng bằng số liệu phỏng vấn/khảo sát thực tế; xác nhận lại bảng giá nhà cung cấp trước khi vận hành chính thức.
