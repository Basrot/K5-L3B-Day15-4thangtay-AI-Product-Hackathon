# Đào data — cách đếm và kết quả

> Điền ở guide bước 1.2. Ôn lại: ngày 2, ngày 6 · lab ngày 2, lab ngày 6.
> Repo chỉ chứa số đã tổng hợp và các ví dụ ẩn danh — không chép lại nguyên file dữ liệu gốc.
> **Tình trạng tệp Excel gốc:** Workbook `.xlsx` của nghiên cứu *Pham et al. (2023)* (`Huong_dan`, `Du_lieu`, `Tu_dien`) được giữ **ngoài repo công khai** theo quy tắc bảo mật dữ liệu (không có trong workspace hiện tại). Các con số dưới đây được trích nguyên trạng từ kết quả đã kiểm chứng trước đó trong `docs/NGHIEN_CUU_VA_DE_XUAT_DE_TAI_TRACK_B.md` (Mục 1.2 và 1.4.2); phần script Python ở cuối Mục 1 dùng để đối chiếu lại trực tiếp khi cung cấp đường dẫn tệp `.xlsx` cục bộ.

## 1. Cách đếm — viết TRƯỚC khi chạy

- Data dùng: Bộ dữ liệu nghiên cứu *Reference intervals of complete blood count and coagulation tests in Vietnamese pregnant women* (*Pham et al., 2023*, Bệnh viện Hùng Vương, TP.HCM, thu thập 06–08/2023, DOI: `https://doi.org/10.1186/s12884-023-06106-2`), sheet `Du_lieu` gồm **867 bản ghi** (`RI0001`–`RI0867`), dùng phân nhóm tam cá nguyệt `trimester_analysis` (`TCN1 < 14w0d`, `TCN2 = 14w0d–28w6d` giữ tuần 28 trong TCN2 theo Bệnh viện Từ Dũ, `TCN3 >= 29w0d`).
- Đếm gì / trên tập nào / lọc gì:
  1. Lọc tập các bản ghi có panel CBC hoàn chỉnh (`cbc_panel_complete == 1`) trên sheet `Du_lieu` (loại 30 dòng thiếu CBC, không tự điền `0` vào ô trống).
  2. Đếm số thai phụ khỏe mạnh có `HGB < 12.0 g/dL` (`< 120 g/L`) — tương ứng tỷ lệ bị gắn cờ "thiếu máu" sai nếu phiếu phòng xét nghiệm áp dụng ngưỡng nữ trưởng thành không mang thai của WHO 2024.
  3. Đếm số thai phụ khỏe mạnh có `HGB` dưới ngưỡng sàng lọc thiếu máu thai kỳ WHO 2024 (`< 11.0 g/dL` ở TCN1/TCN3; `< 10.5 g/dL` ở TCN2), tách theo từng tam cá nguyệt.
  4. Đếm số dòng bị loại ngoại lai (`ri_excluded_analytes`, Dixon `D/R >= 1/3`) trên 8 chỉ số CBC được chọn (`HGB`, `RBC`, `HCT`, `MCV`, `MCH`, `MCHC`, `WBC`, `PLT`).
- **Mẫu số là gì:** **`N = 837` panel CBC hoàn chỉnh** (gồm `287` TCN1 + `273` TCN2 + `277` TCN3; tách riêng khỏi `867` tổng bản ghi vì `30` dòng chỉ có dữ liệu đông máu/thiếu CBC).
- Script / công thức (dùng để tái lập khi có tệp `.xlsx` ngoài repo):

```python
# Chạy cục bộ khi cung cấp đường dẫn workbook .xlsx ngoài repo (không lưu .xlsx vào repo)
import openpyxl

wb = openpyxl.load_workbook("EXTERNAL_HUNG_VUONG_CBC.xlsx", data_only=True)
ws = wb["Du_lieu"]
headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
idx = {h: i for i, h in enumerate(headers)}

cbc_rows = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[idx["cbc_panel_complete"]] == 1]
N = len(cbc_rows)  # Kỳ vọng: 837 (287 TCN1, 273 TCN2, 277 TCN3)
flagged_non_preg = sum(1 for r in cbc_rows if r[idx["HGB"]] < 12.0)  # Kỳ vọng: 416 / 837 (49.70%)
below_who_preg = sum(
    1 for r in cbc_rows
    if r[idx["HGB"]] < (10.5 if r[idx["trimester_analysis"]] == 2 else 11.0)
)  # Kỳ vọng: 95 / 837 (11.35%)
```

## 2. Đọc trước, đếm sau

Đã đọc mô tả cấu trúc 3 sheet (`Huong_dan` 22×2, `Du_lieu` 868×32 gồm 1 tiêu đề + 867 bản ghi, `Tu_dien` 33 dòng định nghĩa cột) và toàn bộ bảng kết quả trích xuất tại `docs/NGHIEN_CUU_VA_DE_XUAT_DE_TAI_TRACK_B.md` (Mục 1.2). Các *kiểu* hiện tượng thấy được trước khi đếm:
- **Pha loãng máu sinh lý rõ rệt ở TCN2:** Khoảng 2.5th–97.5th của `HGB` thai phụ khỏe mạnh tại BV Hùng Vương giảm từ `10.33–13.95 g/dL` (TCN1) xuống `9.71–13.17 g/dL` (TCN2) rồi `9.80–13.97 g/dL` (TCN3) — thấp hơn đáng kể so với cận dưới `12.0 g/dL` của nữ trưởng thành không mang thai.
- **Tăng bạch cầu trung tính sinh lý & dị thường nhập liệu thật:** `WBC` (`6.22–15.55 × 10^9/L`) và `NEUT_abs` (`3.43–12.25 × 10^9/L`) thường vượt ngưỡng `10.0 × 10^9/L` của phiếu người lớn; dữ liệu thật còn có dị thường tuổi thai (`12w7d`, `1w2d`), bản ghi lặp kỹ thuật (`P0613`, `P0798`), theo dõi dọc (`P0756`) và `5` bản ghi bị loại ngoại lai ở các chỉ số ngoài bộ 8 chỉ số (`MONO`, `BASO`, `EOS`, `RDW-SD`, `APTT`).

## 3. Kết quả

| Đếm gì | x / N | % | Ghi chú |
|---|---|---|---|
| Thai phụ khỏe mạnh có `HGB < 12.0 g/dL` (bị gắn cờ thiếu máu sai nếu dùng ngưỡng nữ không mang thai WHO 2024) | 416 / 837 | 49.70% | Trích từ `NGHIEN_CUU_VA_DE_XUAT_DE_TAI_TRACK_B.md` §1.4.2 *(chờ chạy script đối chiếu trực tiếp nếu gắn `.xlsx` ngoài repo)* |
| Thai phụ khỏe mạnh có `HGB` dưới ngưỡng sàng lọc thai kỳ WHO 2024 (`<11.0` TCN1/3; `<10.5` TCN2) | 95 / 837 | 11.35% | Khớp tỷ lệ ~11% nêu trong *Pham et al. (2023)* |
| — Tách riêng TCN1 (`< 11.0 g/dL`) | 22 / 287 | 7.67% | RI 2.5th–97.5th TCN1: `10.33–13.95 g/dL` |
| — Tách riêng TCN2 (`< 10.5 g/dL`) | 28 / 273 | 10.26% | RI 2.5th–97.5th TCN2: `9.71–13.17 g/dL` |
| — Tách riêng TCN3 (`< 11.0 g/dL`) | 45 / 277 | 16.25% | RI 2.5th–97.5th TCN3: `9.80–13.97 g/dL` |
| Ngoại lai bị loại (`ri_excluded_analytes`, Dixon `D/R >= 1/3`) trên 8 chỉ số CBC chọn lọc | 0 / 837 | 0.00% | Cả 5 ca ngoại lai (`RI0205`, `RI0352`, `RI0390`, `RI0616`, `RI0796`) đều nằm ngoài 8 chỉ số |

## 4. ≥5 ví dụ cụ thể (mã dòng / mã đã ẩn danh, không đoán ai là ai)

1. **`RI0601`** (thuộc nhóm trùng lặp kỹ thuật `P0613` / `S0784`, TCN2 `21w3d`): `HGB = 11.94 g/dL`, `WBC = 8.968 × 10^9/L`, `PLT = 300.9 × 10^9/L` — thai phụ khỏe mạnh nhưng `HGB < 12.0 g/dL`, dễ bị đánh dấu thấp nếu phiếu dùng ngưỡng người không mang thai.
2. **`P0756`** (theo dõi dọc 2 lần khám ở TCN2: `RI0713` tại `21w5d` có `HGB = 10.36 g/dL`, `WBC = 10.427 × 10^9/L`, `PLT = 286.4 × 10^9/L`; và `RI0280` tại `28w4d` có `HGB = 11.2 g/dL`, `WBC = 10.616 × 10^9/L`, `PLT = 296 × 10^9/L`) — cho thấy `HGB` dao động quanh ngưỡng `10.5 g/dL` và `WBC > 10.0` ở thai phụ khỏe mạnh.
3. **`RI0114`** (TCN1): tuổi thai ghi `12w7d` (`d = 7 >= 7`, tương đương `13w0d` / 91 ngày; tương tự `RI0862`) — ví dụ dị thường nhập liệu tuổi thai thực tế đòi hỏi Rule Engine phải bắt lỗi `d >= 7`.
4. **`RI0335`** (TCN1): tuổi thai ghi `1w2d` (9 ngày) — ví dụ giá trị quá sớm về mặt sinh học cho lấy máu khám thai, cần gắn cờ hỏi xác nhận lại ngày kinh cuối hoặc siêu âm theo quy tắc Bệnh viện Từ Dũ.
5. **`RI0205`** (TCN1 `12w1d`): bị loại ngoại lai ở `MONO_abs = 3.388`, `MONO_pct = 27.85%`, `BASO_abs = 0.234`, `BASO_pct = 1.93%` — minh họa lý do tách riêng các dòng bạch cầu phụ dễ ngoại lai khỏi phạm vi 8 chỉ số CBC cốt lõi.

## 5. Giới hạn của data

Data cho biết người ta **làm gì / chỉ số xét nghiệm thực tế phân bố thế nào**, không cho biết **vì sao thai phụ thấy vướng hay mất bao lâu để tự đọc phiếu**. Thiếu gì, lệch về phía nào:
- **Giới hạn tệp gốc:** Workbook `.xlsx` gốc giữ ngoài repo công khai nên các con số trên chưa thể chạy tái lập trực tiếp bằng script trong repo nếu người kiểm tra chưa gắn tệp `.xlsx` cục bộ.
- **Giới hạn quần thể & thiết bị:** Chỉ phản ánh thai phụ đơn thai khỏe mạnh tại Bệnh viện Hùng Vương đo trên máy Beckman Coulter DxH 900 (bảng 4 *Pham et al., 2023* chỉ ra RI thất bại khi chuyển giao sang máy khác như Sysmex XE-2100); đồng thời gồm `2` cặp trùng kỹ thuật (`P0613`, `P0798`) và chưa chứa lời kể trực tiếp của thai phụ về việc đọc phiếu ở nhà.
→ Kiểm lại bằng phỏng vấn / khảo sát nào: Kiểm lại bằng phỏng vấn **`≥ 3` thai phụ ngoài nhóm** (`evidence/interviews/PLAN.md`, `P1.md`–`P3.md`) để đo tần suất đọc phiếu trong 1 tháng qua, số phút tra cứu mỗi lần và cách xử lý thực tế.
