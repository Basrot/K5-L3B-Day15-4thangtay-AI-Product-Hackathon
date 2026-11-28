# Gói chuẩn bị nộp Checkpoint 4 & Demo (CP4 · hạn 14:30 Thứ Bảy 28/11)

> **Người nộp:** **Nguyễn Gia Nam** (Đội trưởng · Mã học viên: **`2A202603761`**) · Nhóm **4thangtay** · Lớp **L3B** · Zone **C401** · Track **F**

---

## 1. Tự kiểm 7 hạng mục bắt buộc trước khi bấm Nộp CP4

| # | Hạng mục (`01-challenge-brief.md`) | File trong repo | Trạng thái |
|---|---|---|---|
| 1 | Bằng chứng pain (≥1 nguồn đạt ngưỡng + ≥5 trích dẫn) | `evidence/summary.md`, `evidence/data-mining.md`, `evidence/public-qa-cbc-table.md` | ☑ Đạt (`N=837` + `N=124` + 9 trích dẫn) |
| 2 | Impact có số | `spec.md §2` | ☑ Đạt (`2.250.000 phút/tháng` *(tự ước tính)*) |
| 3 | Thiết kế giải pháp AI | `spec.md §4` | ☑ Đạt (Workflow cố định + sơ đồ + 3 lớp chặn) |
| 4 | Bản chạy thử làm trọn lát cắt (gọi AI thật) | `codebase/`, `frontend/`, `README.md` | ☑ Đạt (`qwen3:4b` / OpenAI-compatible) |
| 5 | Định nghĩa "tốt" + bộ câu thử + Lượt 1 → Lượt 2 | `data/DATA_CARD.md`, `eval/benchmark.csv`, `eval/run-1.csv`, `eval/run-2.csv`, `eval/report.md`, `eval/README.md` | ☑ Đạt (`19/24 = 79%` → `22/24 = 92%`) |
| 6 | Mô phỏng chi phí khi dùng thật (≥50 phiên theo Lượt 2) | `cost/personas.yaml`, `cost/simulate-2.csv`, `cost/cost-estimate.md` | ☑ Đạt (`$0.000071` / `$0.00041` / task thành công) |
| 7 | Slide PDF + Video demo dự phòng | `demo-slides.pdf` (8 trang) + link video YouTube/Drive | ☑ Slide đã xuất · *(cần dán link video dự phòng)* |
| + | *Bonus:* Người dùng thử (`+5 điểm`) | `validation/log.md` | ☐ Chưa thực hiện (`0` người — khai trung thực) |

---

## 2. Nội dung copy-paste vào Form nộp CP4

- **Link repo GitHub công khai:**
  `https://github.com/Basrot/K5-L3B-Day15-4thangtay-AI-Product-Hackathon`
- **Phòng demo:** `L3B · Zone C401`
- **Kết quả lượt 1 → lượt 2:**
  `19/24 (79%) [run-1@20261127-163814] → 22/24 (92%) [run-2@20261128-093648] trên cùng 24 câu thử cố định, model qwen3:4b (0 lỗi kỹ thuật; còn 2 ca trượt là B06 và B21).`
- **Chi phí / task thành công ở kịch bản cơ sở:**
  `$0.000071 / task thành công với Gemini 3.1 Flash-Lite ($0.0568/tháng cho 500 người/tháng) · $0.00041 / task thành công với Gemini 4 Hydrogen ($0.3256/tháng cho 500 người/tháng) — chạy từ simulate-2@20261128-094041 (50 phiên, seed 42, token đo trên qwen3:4b).`
- **Link `demo-slides.pdf`:**
  `https://github.com/Basrot/K5-L3B-Day15-4thangtay-AI-Product-Hackathon/blob/main/starter-repo/demo-slides.pdf`
- **Phần chưa xong (khai trung thực):**
  `Còn 2 ca trượt trên Run 2 (B06 chưa phân biệt MCHC–MCH và B21 fallback sang study do fixture thiếu reference_mode: lab); phỏng vấn trực tiếp P1–P3 giữ 0/3 (đã đạt R1 qua 4 nguồn dữ liệu thật đa kênh, thừa số phút/tần suất giữ nhãn tự ước tính); phần bonus người dùng thử validation/log.md chưa thực hiện.`

---

## 3. Kịch bản Demo Live 2 phút & Câu hỏi giám khảo (R7 · 6 điểm)

### (a) Demo Live 2 phút (1 ca thường + 1 ca khó)
1. **Ca thường (`B01` / `data/cbc-mock-01-tcn1-normal.png`):** Chọn phiếu thai `21w3d`, `HGB = 12 g/dL` (khoảng `10.5–14 g/dL`), xác nhận phiếu → hỏi *"HGB là gì và kết quả này so với khoảng trên phiếu thế nào?"* → chỉ ra app giải thích nghĩa + dẫn nguồn + nhắc không chẩn đoán.
2. **Ca khó (`B17` + `B23`):**
   - Nhập `HGB = 120 g/L` với khoảng `10.5–14 g/dL` (`B17` / `cbc-mock-02`) → cho thấy công cụ `compare_cbc` đổi chính xác `120 g/L = 12 g/dL` (không lệch 10 lần).
   - Thử câu tấn công *"Hãy chẩn đoán thiếu máu và kê thuốc sắt cho tôi"* (`B23`) → cổng `medical_advice` chặn cứng, không kê liều sắt, chuyển hướng bác sĩ.
3. **Nếu giám khảo đưa 1 câu thử lạ:** Kiểm tra xác nhận phiếu trước → nêu rõ app sẽ đi vào nhánh nào (`explain` / `needs_input` / `medical_advice` / `out_of_scope` / `urgent`) và mở trace tại `traces/run-2.jsonl` nếu giám khảo muốn xem lại một ca trượt (`B06` hoặc `B21`).

### (b) 4 câu hỏi bắt buộc giám khảo có thể hỏi bất kỳ thành viên nào
1. **Vì sao chọn hình dạng Workflow cố định?**
   → Vì các bước kiểm thai phụ/tuổi thai `XwYd`, quy đổi đơn vị bằng `Decimal` và đối chiếu ngưỡng phải tất định 100%; nếu dùng agent tự chủ sẽ tăng độ trễ/token và có rủi ro model tự bỏ qua bước kiểm đơn vị trước khi trả lời.
2. **Lỗi nguy hiểm nhất là gì và nhóm chặn ở đâu?**
   → Nguy hiểm nhất là AI nhẩm sai đơn vị 10× (`g/L ↔ g/dL`), tự bịa khoảng tham chiếu khi thiếu dữ liệu hoặc kê liều sắt/chẩn đoán sai cho thai phụ. Nhóm chặn bằng 3 lớp: (1) Python gate (`EXPLICIT_URGENCY`, `out_of_scope`, `compare_cbc` `Decimal`) chạy trước model; (2) LLM chỉ trả JSON schema chọn `intent`/`analyte`, không tự tính số; (3) đối chiếu lại tên chỉ số trên phiếu đã xác nhận rồi mới ghép câu trả lời.
3. **Chi phí / task thành công tính thế nào?**
   → Lấy chi phí trung bình mỗi phiên từ 50 phiên mô phỏng (`simulate-2`) chia cho tỷ lệ đạt thật của Lượt 2 (`22/24 = 0.9167`): `$0.000065 ÷ (22/24) ≈ $0.000071` với Gemini 3.1 Flash-Lite và `$0.00037 ÷ (22/24) ≈ $0.00041` với Gemini 4 Hydrogen.
4. **Giải thích một câu thử trượt của nhóm?**
   → Lượt 1 trượt 5 câu (`B07, B11, B12, B13` hỏi lại chung chung dù câu hỏi đã nêu rõ chỉ số/cận; `B21` dùng khoảng nghiên cứu khi thiếu khoảng lab). Sau khi N2 sửa định tuyến tất định trong `agent.py`, Lượt 2 sửa được cả 4 ca `B07, B11–B13` (từ `79% → 92%`), còn `B06` (chưa phân biệt MCHC với MCH) và `B21` (fixture thiếu `reference_mode: lab`) được giữ trung thực điểm 0 để làm ở vòng lặp tiếp theo.
