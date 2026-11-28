# Dàn slide → lấy số từ file nào

> Làm ở guide bước 5.1. Luật: **không có bằng chứng thì không có slide** — mỗi trang ≥1 con số / trích dẫn có nguồn / kết quả đo.
> Đã xuất PDF thành [`demo-slides.pdf`](../demo-slides.pdf) ở thư mục gốc `starter-repo/` (nguồn HTML: [`slides/demo-slides.html`](demo-slides.html)). Nộp PDF, không nộp link.

| # | Trang | Có gì | Số lấy từ | Xong |
|---|---|---|---|---|
| 1 | Người dùng & pain | Ai · việc gì · chỗ đau + số (`49.70%`, `87.10%`, `95.16%`) và 3 trích dẫn ẩn danh | `evidence/summary.md` | ☑ |
| 2 | Vì sao chọn bài này | Bảng impact rút gọn (`2.250.000 phút/tháng` *(tự ước tính)*) + 2 hướng bị loại + số Bộ Y tế/Từ Dũ | `spec.md` §2 | ☑ |
| 3 | Giải pháp | Lát cắt một câu · sơ đồ SVG Workflow cố định · mức tự động · 4 điều không làm · 3 lớp chặn | `spec.md` §4 | ☑ |
| 4 | Demo live | Phiếu `SYN-02` (`cbc-mock-02`) + ca thường `B01` + ca khó `B17` (đổi đơn vị) & `B23` (chặn kê thuốc) + dự phòng | `eval/benchmark.csv`, `eval/run-2.csv`, `data/` | ☑ |
| 5 | **Đánh giá thế nào** | 24 câu · 3 metric · chấm chéo 5/5 · `run-1` (`79%`) → `run-2` (`92%`) + lỗi `B06, B21` | `eval/README.md`, `eval/report.md` | ☑ |
| 6 | **Chi phí khi dùng thật** | `$0.000071 / $0.00041` / task thành công · 3 kịch bản (`100/500/1.500`) · so với `22.5` phút/người/tháng | `cost/cost-estimate.md`, `simulate-2` | ☑ |
| 7 | Kết luận | **ITERATE** trước khi mở cho bệnh nhân thật (GO nguyên mẫu kiểm soát) — dẫn số trang 1, 5, 6 | `summary.md`, `report.md`, `quality-and-safety.md` | ☑ |
| 8 | Nếu có thêm 1 tuần | Sửa `B06/B21` + Lượt 3, đo OCR exact-match & chi phí hệ thống, phỏng vấn `P1–P3` & bác sĩ | `eval/report.md` §4 · `validation/log.md` | ☑ |

**Trước khi lên:** tải repo về một máy khác (hoặc thư mục mới), chạy theo mục "Chạy trong 3 phút" của `README.md` · `.env` có trên máy demo, đã gọi thử 1 câu trong vòng 1 giờ trước giờ demo · video dự phòng mở được bằng cửa sổ ẩn danh · biết bản chạy thử sẽ làm gì với **1 câu thử lạ** của giám khảo.

## Phân công trình bày (mỗi thành viên ≥ 1 phần)

| Trang | Nội dung chính | Người nói |
|---|---|---|
| Trang 1–2 | Người dùng, bằng chứng pain đa nguồn (`N=837`, `N=124`), Impact & 2 hướng bị loại | **Đào Ngọc Hân (N1)** |
| Trang 3 | Lát cắt, sơ đồ Workflow cố định, `compare_cbc` `Decimal` & 3 lớp chặn an toàn | **Nguyễn Gia Nam (N2 · Đội trưởng)** |
| Trang 4 | Demo live (ca thường `B01` + ca khó `B17` / `B23` + xử lý câu thử lạ của giám khảo) | **Trần Trọng Đức Tài (N4)** & **Nguyễn Gia Nam (N2)** |
| Trang 5–6 | Bộ 24 câu thử, chấm chéo 5/5, kết quả `run-1 → run-2` (79% → 92%) & Chi phí 3 kịch bản | **Thiều Thế Ngọc (N3)** |
| Trang 7–8 | Kết luận **ITERATE** & 3 ưu tiên nếu có thêm 1 tuần | **Đào Ngọc Hân (N1)** / **Nguyễn Gia Nam (N2)** |
