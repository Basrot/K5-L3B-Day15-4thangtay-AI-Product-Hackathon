# Gói nội dung nộp Checkpoint 2 (CP2 · hạn 19:30 Thứ Sáu 27/11)

> **Người nộp:** **Nguyễn Gia Nam** (Đội trưởng · Mã học viên: **`2A202603761`**) · Nhóm **4thangtay** · Lớp **L3B** · Zone **C401** · Track **F**

---

## 1. Danh sách link cần dán vào Form nộp CP2

*(Kiểm tra repo ở chế độ **Public** bằng cửa sổ ẩn danh sau khi push.)*

- **Link repo:** `https://github.com/Basrot/K5-L3B-Day15-4thangtay-AI-Product-Hackathon`
- **Link `canvas.md`:** `https://github.com/Basrot/K5-L3B-Day15-4thangtay-AI-Product-Hackathon/blob/main/starter-repo/canvas.md`
- **Link `spec.md` (có sơ đồ kiến trúc §4 & chuẩn "đạt" §7):** `https://github.com/Basrot/K5-L3B-Day15-4thangtay-AI-Product-Hackathon/blob/main/starter-repo/spec.md`
- **Link `eval/benchmark.csv` (24 câu thử):** `https://github.com/Basrot/K5-L3B-Day15-4thangtay-AI-Product-Hackathon/blob/main/starter-repo/eval/benchmark.csv`
- **Link `eval/metric_spec.yaml` (3 metric):** `https://github.com/Basrot/K5-L3B-Day15-4thangtay-AI-Product-Hackathon/blob/main/starter-repo/eval/metric_spec.yaml`
- **Link `eval/README.md` & chấm chéo `5/5`:** `https://github.com/Basrot/K5-L3B-Day15-4thangtay-AI-Product-Hackathon/blob/main/starter-repo/eval/README.md`
- **Link `data/DATA_CARD.md` (bản đầu):** `https://github.com/Basrot/K5-L3B-Day15-4thangtay-AI-Product-Hackathon/blob/main/starter-repo/data/DATA_CARD.md`

---

## 2. Nội dung copy-paste vào từng ô trên Form CP2

### (a) Canvas cập nhật + 1–3 dòng "Đã đổi gì so với CP1"
- **Track & lát cắt:** Track F (Làn khác — Đọc hiểu xét nghiệm CBC thai kỳ) · Một thai phụ Việt Nam trưởng thành xác nhận phiếu kết quả CBC theo tuần thai ở tam cá nguyệt 1–3, công cụ quy tắc đối chiếu với khoảng trên phiếu hoặc khoảng nghiên cứu theo tam cá nguyệt rồi AI chọn dòng liên quan để giải thích ý nghĩa chỉ số bằng tiếng Việt có dẫn nguồn và gợi ý câu hỏi trao đổi với bác sĩ sản khoa.
- **Đã đổi gì so với CP1:**
  1. Chốt phạm vi giải thích gồm đúng **8 chỉ số CBC trọng tâm** (`HGB, RBC, HCT, MCV, MCH, MCHC, WBC, PLT`) đồng bộ giữa 3 phiếu giả lập N1, bộ 24 câu thử N3 và `codebase/` N2.
  2. Bổ sung chế độ đối chiếu `study` tự tra khoảng nghiên cứu *Pham et al. (2023)* theo tam cá nguyệt bên cạnh chế độ `lab` theo khoảng in trên phiếu.
  3. Hoàn thành thống kê đào dữ liệu đầu tiên (`416/837 = 49.70%` và `95/837 = 11.35%`), khóa bộ 24 câu thử + 3 metric + chuẩn "đạt" (chấm chéo N1–N3 trên `run-1.csv` khớp **`5/5`**).

### (b) Nguồn bằng chứng đang làm & tiến độ
- **Nguồn 1 — Đào dữ liệu công bố (`evidence/data-mining.md`):** Đã hoàn tất bước đếm chính trên `N = 837` panel CBC thai phụ khỏe mạnh tại BV Hùng Vương (*Pham et al., 2023*): **`416/837 (49.70%)`** có `HGB < 12.0 g/dL` (bị gắn cờ thiếu máu sai nếu phiếu dùng ngưỡng nữ không mang thai) và **`95/837 (11.35%)`** dưới ngưỡng sàng lọc WHO 2024, kèm 5 ví dụ ẩn danh (`RI0601`, `P0756`, `RI0114`, `RI0335`, `RI0205`).
- **Nguồn 2 — Phỏng vấn kiểm chéo (`evidence/interviews/PLAN.md` & `evidence/summary.md`):** Đã chốt bộ 7 câu hỏi Mom Test (không thu ảnh phiếu thật/PII) và lịch phỏng vấn 3 thai phụ ngoài nhóm (`P1` TCN1, `P2` TCN2, `P3` TCN3/mới sinh `≤3 tháng`) triển khai tối 27/11 – sáng 28/11 trước CP3.

### (c) Chuẩn "đạt" bằng số (chép từ `spec.md` §7 — KHÓA CỨNG tại CP2, không sửa về sau)
> **"Đạt khi ≥ 90% tổng số câu thử qua, đồng thời 100% ca thiếu dữ kiện hoặc ngoài phạm vi đi đúng nhánh, 100% ca có giá trị và đơn vị hợp lệ được đối chiếu đúng theo đáp án, và ít nhất 90% ca giải thích bám đúng dòng và dữ kiện trên phiếu."**

- *Thông tin bổ sung đã có sớm cho CP3:* Chấm chéo 5 mẫu trên `eval/run-1.csv` (`B01, B07, B11, B19, B23`) giữa N3 & N1 đạt đồng thuận **`5/5 (100%)`** (`eval/calibration-5-samples.md`). Lượt 1 với model thật `qwen3:4b` (Ollama local) đạt **`19/24 (79%)`** (`run-1@20261127-163814`, còn 5 lỗi ở `B07, B11, B12, B13, B21` chuyển N2 sửa trước lượt 2).

### (d) Bản chạy thử dạng khung
- Đã chạy `python run.py` ở chế độ AI giả (`MODEL_PROVIDER=fake`) đi hết luồng và đã nối model thật `qwen3:4b` qua Ollama local cho lượt 1 (`run-1@20261127-163814`) cùng mô phỏng chi phí 50 phiên (`simulate-1@20261127-164346`).

---

## 3. Việc cần làm tay trước khi bấm Nộp (19:30)

1. **Nhắn N3 (Thiều Thế Ngọc) push `eval/run-1.csv`, `traces/run-1.jsonl`, `cost/simulate-1.csv`, `cost/simulate-1-summary.md`:** File `.gitignore` gốc đã được gỡ chặn 3 thư mục này để GitHub nhận đúng các file kết quả lượt 1 (tránh lỗi 404 như lần PR #5 trước đó).
2. **Commit & Push phần hợp nhất hiện tại + Kiểm ẩn danh:** `git add` → `git commit` → `git push` lên `main`, mở thử các link ở Mục 1 bằng cửa sổ ẩn danh rồi đội trưởng Nguyễn Gia Nam (`2A202603761`) copy nội dung điền Form CP2.
