# N1 Handoff Summary — Đào Ngọc Hân (`2A202603779`, Track B)

> Tài liệu bàn giao cho **N2 (Nguyễn Gia Nam)**, **N3 (Thiều Thế Ngọc)** và **N4 (Trần Trọng Đức Tài)** tại các mốc **CP1–CP3**, tổng hợp toàn bộ đầu ra N1 có thể hoàn thành ngoại tuyến trên máy cục bộ và các phần đang bị chặn do thiếu dữ liệu bên ngoài.

---

## 1. Danh mục đầu ra CP1–CP3 do N1 đã hoàn thành

| Mốc | Tệp trong `starter-repo/` | Nội dung chính |
|---|---|---|
| **CP1** | `evidence/hypothesis.md` | Giả thuyết ban đầu (không chứa "AI"), giải thích thay thế, ngưỡng định lượng kiểm chứng (`≥30%` gắn cờ sai, `≥2/3` phỏng vấn), nguồn sẽ kiểm. |
| **CP1** | `canvas.md` | Đủ 7 dòng bản đầu (`4thangtay · Track B`); dòng 3 pain 1 câu không chữ "AI"; dòng 5 lát cắt đúng 1 câu (`1 người dùng · 1 việc · 1 quyết định AI · 1 kết quả`); dòng CP2 để `[Chờ cập nhật tại CP2]`. |
| **CP1** | `evidence/interviews/PLAN.md`, `P1.md`–`P3.md` | Kế hoạch & bộ 7 câu hỏi Mom Test dành cho thai phụ từng đọc phiếu CBC trong 1 tháng qua (hỏi thời gian đọc/lần, cách xoay xở, cấm thu ảnh phiếu thật/PII); các phiếu `P1`–`P3` giữ trống chờ phỏng vấn thật. |
| **CP2** | `data/DATA_CARD.md` | Khai báo Dataset 1 (*Pham et al. 2023*, `867` bản ghi → `837` CBC, BV Hùng Vương, DOI URL, `.xlsx` gốc ngoài repo; kèm WHO 2024, Từ Dũ, MedlinePlus), Dataset 2 (`3` phiếu giả lập gắn nhãn `synthetic`, cách sinh & kiểm 24/24 dòng) và quy tắc No-PII. |
| **CP3** | `evidence/data-mining.md` | Công thức & mẫu số (`N = 837`), số liệu kiểm chứng (`416/837 = 49.70%` dưới `12.0 g/dL`; `95/837 = 11.35%` dưới WHO 2024; `0` ngoại lai ở 8 chỉ số chọn), 5 ví dụ ẩn danh (`RI0601`, `P0756`, `RI0114`, `RI0335`, `RI0205`), và khai báo `.xlsx` gốc giữ ngoài repo. |
| **CP3** | `evidence/summary.md` | Khung tổng hợp bằng chứng + bảng lịch hẹn `P1–P3`; phần số đào data đã điền đủ, phần phỏng vấn thật & trích dẫn người dùng giữ `[Chờ phỏng vấn P1–P3]` (không bịa dữ liệu). |
| **CP3** | `spec.md` (`header` + `§0–§2`) | Luồng hiện tại 4 bước, JTBD & Pain không chữ "AI", bảng 3 hướng (`Hướng B` chọn, giữ nguyên `Hướng A` & `Hướng C` bị loại kèm lý do), công thức `Impact / tháng` có nguồn hoặc `*(tự ước tính)*`. **Giữ nguyên hoàn toàn `§4` và `§5–§10`.** |
| **CP3** | `eval/n1-candidate-cases.csv` | 10 tình huống ứng viên ẩn danh (đủ 6 cột chuẩn `benchmark.csv`) phủ đủ 8 chỉ số CBC để N3 chọn ghép vào `eval/benchmark.csv`. |

---

## 2. Bộ 3 phiếu CBC giả lập + JSON đáp án (cho N2 & N4)

Các tệp đặt trong `starter-repo/data/` (tương thích cấu trúc `data/cbc-demo-input.json`, gắn watermark `"MẪU GIẢ LẬP (SYNTHETIC) — KHÔNG PHẢI PHIẾU XÉT NGHIỆM THẬT"`):

1. **`starter-repo/data/cbc-mock-01-tcn1-normal.png` + `.json`** — Thai kỳ TCN1 (`10w4d`, `pregnant`, `adult_confirmed: true`), 8 chỉ số bình thường theo RI TCN1 BV Hùng Vương (`HGB 11.6 g/dL` nhưng bị đánh dấu L nếu so khoảng người lớn `12.0–15.5 g/dL`).
2. **`starter-repo/data/cbc-mock-02-tcn2-borderline-unitmix.png` + `.json`** — Thai kỳ TCN2 (`24w2d`), cố ý trộn đơn vị **`HGB 104 g/L`** vs khoảng tham chiếu **`12.0–15.5 g/dL`** (lệch 10×, sát biên WHO 2024 `< 105 g/L` nhưng trong RI TCN2 `9.71–13.17 g/dL`), kèm tăng bạch cầu sinh lý (`WBC 12.8 10^9/L`, `NEUT_abs 8.9 10^9/L`).
3. **`starter-repo/data/cbc-mock-03-tcn3-microcytic-plt.png` + `.json`** — Thai kỳ TCN3 (`33w1d`), `HGB 10.1 g/dL`, hồng cầu nhỏ nhược sắc (`MCV 75.8 fL`, `MCH 24.4 pg`) và giảm tiểu cầu nhẹ (`PLT 138 10^9/L < 150`).

### Lưu ý đồng bộ quan trọng cho N2 (`codebase/tools.py` & `spec.md §4`)
- Hiện tại `starter-repo/codebase/tools.py` (`ANALYTES` dòng 12, kiểm tra `1 <= len(raw_rows) <= 3` dòng 65) và `spec.md §4` mới hỗ trợ **3 chỉ số** (`HGB`, `WBC`, `PLT`), trong khi yêu cầu đề tài và 3 bộ phiếu giả lập trên phủ đủ **8 chỉ số** (`RBC`, `HGB`, `HCT`, `MCV`, `MCH`, `WBC`, `NEUT_abs`, `PLT`).
- **Cách phối hợp:**
  - Nếu giữ phạm vi **3 chỉ số** ở bản chạy thử CP2: N2/N4 chỉ cần lọc lấy 3 dòng `{HGB, WBC, PLT}` từ `report.rows` của các file `cbc-mock-01..03*.json` để đưa vào `compare_cbc()`.
  - Nếu nâng cấp lên **8 chỉ số** trước CP3: N2 mở rộng `ANALYTES`, bảng đơn vị (`RBC`, `HCT %/L`, `MCV fL`, `MCH pg`, `NEUT_abs`), bỏ giới hạn `<= 3` dòng trong `tools.py`, và cập nhật `spec.md §4` (cùng `tests/test_cbc_ai.py`).

---

## 3. Bộ 10 câu hỏi ứng viên cho N3 (`eval/n1-candidate-cases.csv`)

- **Tệp bàn giao:** `starter-repo/eval/n1-candidate-cases.csv` (10 dòng `N1_C01`–`N1_C10`, giữ nguyên cấu trúc 6 cột `id,input,expected,pass_criterion,type,source` của `eval/benchmark.csv`).
- **Phân bổ:** `2 thuong`, `6 kho`, `2 tu_choi` (đều là kịch bản tấn công/ngoài phạm vi); nguồn gồm `2 data_that` (ẩn danh từ *Pham et al. 2023*), `3 sinh_seed` (khớp 3 phiếu `cbc-mock-01..03`), `5 tu_viet` (trong đó 2 ca lỗi thiếu đơn vị/mâu thuẫn có ghi `[Chờ gắn nguoi_dung: P_ sau phỏng vấn]`).
- **Lưu ý cho N3:** `eval/benchmark.csv` và `eval/metric_spec.yaml` được N1 giữ nguyên để N3 chủ động hợp nhất, bổ sung đủ `20–30` câu (đảm bảo `≥ 1/3` nguồn từ `nguoi_dung` / `data_that` sau khi có `P1–P3`), điền `≥ 3` metrics và **khóa trước 19:30 Thứ Sáu 27/11 (CP2)**.

---

## 4. Các phần đang bị chặn bởi yếu tố bên ngoài (chưa thể hoàn tất cục bộ)

1. **Workbook Excel gốc (*Pham et al., 2023*):** File `.xlsx` (`Huong_dan`, `Du_lieu`, `Tu_dien`) được giữ ngoài repo công khai nên chưa chạy lại trực tiếp được đoạn script đếm trong `evidence/data-mining.md` trên máy này; mọi số liệu đã trích dẫn nguyên trạng từ `docs/NGHIEN_CUU_VA_DE_XUAT_DE_TAI_TRACK_B.md`.
2. **Phỏng vấn người dùng thật (`P1`–`P3`):** Chưa có cuộc phỏng vấn thực tế với 3 thai phụ ngoài nhóm nên các ô kết quả, thời gian đọc phiếu (phút), tần suất/tháng, 5 trích dẫn nguyên văn từ người dùng, phần đối chiếu khớp/lệch và kết luận cuối trong `evidence/summary.md` và `evidence/interviews/P1.md`–`P3.md` buộc phải giữ `[Chờ phỏng vấn P1–P3]`, đồng thời các thừa số thời gian/quy mô trong `spec.md §2` đang ghi rõ `*(tự ước tính)*`.
3. **Chấm chéo & hoàn thiện liên vai trò:** Chấm chéo 5 output mẫu cùng N3 (`≥ 4/5`), cập nhật ô CP2 trong `canvas.md`, hoàn thiện `TEAMS.md` cho N3/N4, mở rộng/đồng bộ `codebase/tools.py` (3 vs 8 chỉ số) và tích hợp UI đọc/xác nhận phiếu cho N4.
