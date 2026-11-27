# N1 Handoff Summary (v1.1 — Đồng bộ `main` `62104b5`) — Đào Ngọc Hân (`2A202603779`, Track B)

> Tài liệu bàn giao đã đồng bộ với bản `main` mới nhất (PR #1 `feat/evaluation-cost`, PR #2 `codex/trimester-reference-intervals`, PR #3 `codex/cbc-explanation-polish`) cho **N2 (Nguyễn Gia Nam)**, **N3** và **N4** tại các mốc **CP1–CP3**.

---

## 1. Danh mục đầu ra CP1–CP3 do N1 đã hoàn thành & đồng bộ

| Mốc | Tệp trong `starter-repo/` | Nội dung chính |
|---|---|---|
| **CP1** | `evidence/hypothesis.md` | Giả thuyết ban đầu (không chứa "AI"), giải thích thay thế, ngưỡng định lượng kiểm chứng (`≥30%` gắn cờ sai, `≥2/3` phỏng vấn), nguồn sẽ kiểm. |
| **CP1** | `canvas.md` | Đủ 7 dòng bản đầu (`4thangtay · Track B`) theo danh mục 8 chỉ số chuẩn (`HGB, RBC, HCT, MCV, MCH, MCHC, WBC, PLT`); pain không chữ "AI"; lát cắt đúng 1 câu; dòng CP2 để `[Chờ cập nhật tại CP2]`. |
| **CP1** | `evidence/interviews/PLAN.md`, `P1.md`–`P3.md` | Kế hoạch & bộ 7 câu hỏi Mom Test dành cho thai phụ từng đọc phiếu CBC trong 1 tháng qua (hỏi thời gian đọc/lần, cách xoay xở, cấm thu ảnh phiếu thật/PII); các phiếu `P1`–`P3` giữ trống chờ phỏng vấn thật. |
| **CP2** | `data/DATA_CARD.md` | Khai báo Dataset 1 (*Pham et al. 2023*, `867` bản ghi → `837` CBC, BV Hùng Vương, DOI URL, `.xlsx` gốc ngoài repo; kèm WHO 2024, Từ Dũ, MedlinePlus), Dataset 2 (`3` phiếu giả lập `2160×1880` gắn nhãn `synthetic`, khớp 100% `SUPPORTED_ANALYTES`) và quy tắc No-PII. |
| **CP3** | `evidence/data-mining.md` | Công thức & mẫu số (`N = 837`), số liệu kiểm chứng (`416/837 = 49.70%` dưới `12.0 g/dL`; `95/837 = 11.35%` dưới WHO 2024; `0/837` ngoại lai ở 8 chỉ số chọn), 5 ví dụ ẩn danh (`RI0601`, `P0756`, `RI0114`, `RI0335`, `RI0205`), và khai báo `.xlsx` gốc giữ ngoài repo. |
| **CP3** | `evidence/summary.md` | Khung tổng hợp bằng chứng + bảng lịch hẹn `P1–P3`; phần số đào data đã điền đủ, phần phỏng vấn thật & trích dẫn người dùng giữ `[Chờ phỏng vấn P1–P3]`. |
| **CP3** | `spec.md` (`header` + `§0–§2`) | Luồng hiện tại 4 bước, JTBD & Pain không chữ "AI", bảng 3 hướng (`Hướng B` chọn, giữ `Hướng A` & `Hướng C` bị loại kèm lý do, khớp hoàn toàn với `§4` trên `main`), công thức `Impact / tháng` có nguồn hoặc `*(tự ước tính)*`. |
| **CP3** | `eval/n1-candidate-cases.csv` | 10 tình huống ứng viên ẩn danh (`N1_C01`–`N1_C10`, đủ 6 cột chuẩn `benchmark.csv`) phủ đủ 8 chỉ số `SUPPORTED_ANALYTES` + cả 2 chế độ `study` và `lab`, chạy thông 100% qua `codebase.agent.answer()`. |

---

## 2. Bộ 3 phiếu CBC giả lập + JSON đáp án (cho N2 & N4)

Các tệp đặt trong `starter-repo/data/` (phủ đúng 8 mã `RBC, HGB, HCT, MCV, MCH, MCHC, WBC, PLT` trong `SUPPORTED_ANALYTES` & `ANALYTE_EXPLANATIONS`, gắn watermark `"MẪU GIẢ LẬP (SYNTHETIC) — KHÔNG PHẢI PHIẾU XÉT NGHIỆM THẬT"`):

1. **`starter-repo/data/cbc-mock-01-tcn1-normal.png` + `.json`** — Thai kỳ TCN1 (`10w4d`, `pregnant`, `adult_confirmed: true`), 8 chỉ số bình thường theo RI TCN1 BV Hùng Vương (`HGB 11.6 g/dL`, `HCT 34.9%`, `MCHC 33.2 g/dL` nhưng `HGB/HCT` có cờ `L` nếu so khoảng người lớn không mang thai `12.0–15.5 g/dL` / `35.0–45.0%`).
2. **`starter-repo/data/cbc-mock-02-tcn2-borderline-unitmix.png` + `.json`** — Thai kỳ TCN2 (`24w2d`), trộn đơn vị **`HGB 104 g/L`** vs khoảng tham chiếu **`12.0–15.5 g/dL`** (quy đổi thành `10.4 g/dL`), kèm `MCHC 33.0 g/dL` và tăng bạch cầu sinh lý (`WBC 12.8 10^9/L`).
3. **`starter-repo/data/cbc-mock-03-tcn3-microcytic-plt.png` + `.json`** — Thai kỳ TCN3 (`33w1d`), `HGB 10.1 g/dL`, hồng cầu nhỏ (`MCV 75.8 fL`, `MCH 24.4 pg`), `MCHC 32.2 g/dL` và giảm tiểu cầu nhẹ (`PLT 138 10^9/L < 150`).

---

## 3. Các phần còn chờ dữ liệu bên ngoài (tiếp tục ở CP2–CP4)

1. **Phỏng vấn người dùng thật (`P1`–`P3`):** Điền biên bản vào `evidence/interviews/P1.md`–`P3.md`, cập nhật các ô `[Chờ phỏng vấn P1–P3]` trong `evidence/summary.md`, dòng thay đổi CP2 trong `canvas.md`, và bổ sung tối thiểu 8 câu nói ẩn danh từ người dùng cuối (`nguoi_dung: P1..P3`) cho N3 cập nhật nguồn `eval/benchmark.csv`.
2. **Điền vai N3/N4 vào `TEAMS.md`:** Cập nhật cột `Phần việc chính` của Thiều Thế Ngọc và Trần Trọng Đức Tài khi hai bạn chốt vai.
3. **Chấm chéo & Bonus:** Chấm chéo 5 đầu ra mẫu cùng N3 (`≥ 4/5`) trước CP2; ghi `validation/log.md` (nếu có người dùng thử ở CP4) và `reflection/dao-ngoc-han.md` trước `23:59` Thứ Bảy 28/11.
