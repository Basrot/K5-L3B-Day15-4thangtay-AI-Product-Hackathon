# Đào data — cách đếm và kết quả (4 trụ cột đa nguồn)

> Điền ở guide bước 1.2. Ôn lại: ngày 2, ngày 6 · lab ngày 2, lab ngày 6.
> Repo chỉ chứa số đã tổng hợp và các ví dụ ẩn danh (`≤ 2` câu/bài) — không chép lại nguyên file dữ liệu gốc hay toàn văn HTML/PII.

---

## Phần A · Dữ liệu nghiên cứu CBC thai kỳ BV Hùng Vương (*Pham et al., 2023*)

> **Tình trạng tệp Excel gốc:** Workbook `.xlsx` của nghiên cứu *Pham et al. (2023)* (`Huong_dan`, `Du_lieu`, `Tu_dien`) được giữ **ngoài repo công khai** theo quy tắc bảo mật dữ liệu (không có trong workspace hiện tại). Các con số dưới đây được trích nguyên trạng từ kết quả đã kiểm chứng trước đó trong `docs/NGHIEN_CUU_VA_DE_XUAT_DE_TAI_TRACK_B.md` (Mục 1.2 và 1.4.2).

### 1. Cách đếm — viết TRƯỚC khi chạy

- **Data dùng:** Bộ dữ liệu nghiên cứu *Reference intervals of complete blood count and coagulation tests in Vietnamese pregnant women* (*Pham et al., 2023*, Bệnh viện Hùng Vương, TP.HCM, thu thập 06–08/2023, DOI: `https://doi.org/10.1186/s12884-023-06106-2`), sheet `Du_lieu` gồm **867 bản ghi** (`RI0001`–`RI0867`), dùng phân nhóm tam cá nguyệt `trimester_analysis` (`TCN1 < 14w0d`, `TCN2 = 14w0d–28w6d` giữ tuần 28 trong TCN2 theo BV Từ Dũ, `TCN3 >= 29w0d`).
- **Đếm gì / mẫu số:** Lọc `cbc_panel_complete == 1` → **`N = 837` panel CBC hoàn chỉnh** (`287` TCN1 + `273` TCN2 + `277` TCN3; loại `30` dòng thiếu CBC), rồi đếm tỷ lệ có `HGB < 12.0 g/dL` (bị gắn cờ thiếu máu sai theo ngưỡng nữ không mang thai WHO 2024), tỷ lệ dưới ngưỡng sàng lọc thai kỳ WHO 2024 (`<11.0` TCN1/3; `<10.5` TCN2), và ngoại lai Dixon `D/R >= 1/3` trên 8 chỉ số CBC.

```python
# Chạy cục bộ khi cung cấp đường dẫn workbook .xlsx ngoài repo (không lưu .xlsx vào repo)
import openpyxl

wb = openpyxl.load_workbook("EXTERNAL_HUNG_VUONG_CBC.xlsx", data_only=True)
ws = wb["Du_lieu"]
headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
idx = {h: i for i, h in enumerate(headers)}

cbc_rows = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[idx["cbc_panel_complete"]] == 1]
N = len(cbc_rows)  # 837 (287 TCN1, 273 TCN2, 277 TCN3)
flagged_non_preg = sum(1 for r in cbc_rows if r[idx["HGB"]] < 12.0)  # 416 / 837 (49.70%)
below_who_preg = sum(
    1 for r in cbc_rows
    if r[idx["HGB"]] < (10.5 if r[idx["trimester_analysis"]] == 2 else 11.0)
)  # 95 / 837 (11.35%)
```

### 2. Kết quả Phần A (`N = 837`)

| Đếm gì | x / N | % | Ghi chú |
|---|---:|---:|---|
| Thai phụ khỏe mạnh có `HGB < 12.0 g/dL` (bị gắn cờ thiếu máu sai nếu dùng ngưỡng nữ không mang thai WHO 2024) | **416 / 837** | **49.70%** | Khoảng RI TCN2: `9.71–13.17 g/dL` (thấp hơn hẳn ngưỡng `12.0`) |
| Thai phụ khỏe mạnh có `HGB` dưới ngưỡng sàng lọc thai kỳ WHO 2024 (`<11.0` TCN1/3; `<10.5` TCN2) | **95 / 837** | **11.35%** | Khớp tỷ lệ ~11% nêu trong *Pham et al. (2023)* |
| — Tách riêng TCN1 (`< 11.0 g/dL`) / TCN2 (`< 10.5 g/dL`) / TCN3 (`< 11.0 g/dL`) | `22/287` · `28/273` · `45/277` | `7.67%` · `10.26%` · `16.25%` | Tăng rõ ở TCN2–TCN3 do pha loãng máu sinh lý |
| `WBC` sinh lý thai kỳ (`2.5th–97.5th`) | lên tới `14.14–15.55 × 10^9/L` | — | Vượt cận trên `10.0 × 10^9/L` hay in trên phiếu người không mang thai |
| Ngoại lai bị loại (`ri_excluded_analytes`, Dixon `D/R >= 1/3`) trên 8 chỉ số CBC chọn lọc | **0 / 837** | **0.00%** | Cả `5` ca ngoại lai đều nằm ngoài 8 chỉ số (`MONO, BASO, EOS, RDW-SD, APTT`) |

---

## Phần B & C · Đào quy mô lớn Hỏi – Đáp công khai đa nguồn (BV Từ Dũ & Hệ thống MEDLATEC)

### 1. Khung chọn mẫu tiền định (`M_total = 4.166 → N_total = 124`)

- **Ngày thu thập:** `27/11/2026` · **Script tái lập & kiểm chứng:** `python -u evidence/mine_public_qa.py --tudu-pages 300 --med-spk-pages 53 --med-hh-pages 6` và `python evidence/mine_public_qa.py --verify`.
- **Ba khung mẫu độc lập, tách biệt mẫu số:**
  1. **BV Từ Dũ — Sức khỏe mang thai (`https://tudu.com.vn/vn/suc-khoe-mang-thai/`):** Quét tuần tự **`300` trang đầu tiên** → **`M_tudu = 3.586` bài liên tiếp** (`264` ứng viên danh mục, `4` lỗi tải chi tiết). Loại thủ công `12` bài nhiễu không phải CBC (`beta-hCG`, dung nạp 75g đường, hồng cầu nước tiểu, Rubella, Viêm gan B, ĐMDG/mề đay) → **`N_tudu = 85` bài (`TD01`–`TD85`, `2.37%`)**.
  2. **MEDLATEC — Sản phụ khoa (`https://medlatec.vn/hoi-dap/san-phu-khoa-c11534`):** Quét trọn **`53/53` trang** → **`M_med_spk = 529` bài** (`0` lỗi). Lọc `35` ứng viên, loại các ca dịch âm đạo/soi tươi, nước tiểu `70 leu/uL`, `beta-hCG`, `CA125`, `prolactin`, canxi → giữ **`N_spk = 12` bài (`ML01`–`ML12`, `7` bài nêu rõ tuổi thai)**.
  3. **MEDLATEC — Huyết học (`https://medlatec.vn/hoi-dap/huyet-hoc-c11541`):** Quét trọn **`6/6` trang (100% chuyên mục)** → **`M_med_hh = 51` bài** (`0` lỗi). Loại `24` bài ngoài CBC (HIV, VGB, Triple test, xét nghiệm gót chân, ghép tế bào gốc nhi, địa chỉ lấy máu) → giữ **`N_hh = 27` bài (`ML13`–`ML39`, `4` bài thai kỳ)** nhằm đo hành vi bệnh nhân nhận kết quả xét nghiệm qua cổng điện tử/SMS.
- **Tách rạch ròi mẫu số tránh pha trộn quần thể:**
  - **Tập thai kỳ / tiền sản thuần túy (`N_thai = 96`):** `85` BV Từ Dũ + `11` MEDLATEC thai kỳ.
  - **Tập đa nguồn đầy đủ (`N_total = 124`):** `96` ca thai kỳ/tiền sản + `28` ca bệnh nhân đọc bảng CBC 18–32 chỉ số trên kênh xét nghiệm điện tử MEDLATEC (`evidence/public-qa-cbc-table.md`).

### 2. Đọc trước, đếm sau & Kết quả phân bố nhãn (`N_total = 124`)

Khi đọc lướt trước khi gán nhãn, ngoài 4 nhóm hành vi quen thuộc tại BV Từ Dũ (lo lệch ngưỡng/Thalassemia, chép mã kèm lệch đơn vị, hỏi tăng liều sắt, hành chính), chuyên mục Huyết học điện tử MEDLATEC bộc lộ thêm một điểm nghẽn nổi bật: bệnh nhân nhận kết quả online thường thấy **các dòng tô màu xanh, đen bôi đậm, đỏ** trên bảng **18–32 chỉ số** (`ML19`), hoặc bác sĩ khám nhanh không kịp giải thích (`ML24`: *"bảng xét nghiệm này bác sĩ không giải thích gì em không hiểu lắm"*), buộc họ chép số hoặc gửi mã tra cứu lên mạng nhờ giải thích.

| Nhãn chính | BV Từ Dũ (`N = 85`) | Tập thai kỳ gộp (`N = 96`) | MEDLATEC Gộp (`N = 39`) | Toàn bộ đa nguồn (`N = 124`) |
|---|---:|---:|---:|---:|
| `L1_lech_nguong_lo_lang` | 34/85 (40.00%) | 39/96 (40.62%) | 16/39 (41.03%) | **50 / 124 (40.32%)** |
| `L2_lung_tung_ma_va_don_vi` | 10/85 (11.76%) | 12/96 (12.50%) | **17/39 (43.59%)** | **27 / 124 (21.77%)** |
| `L3_hoi_bo_sung_sat_va_xu_tri` | **26/85 (30.59%)** | **30/96 (31.25%)** | 5/39 (12.82%) | **31 / 124 (25.00%)** |
| `L4_khac_hanh_chinh_ngoai_cbc` | 15/85 (17.65%) | 15/96 (15.62%) | 1/39 (2.56%) | **16 / 124 (12.90%)** |
| **Đau & nhu cầu đọc hiểu trực tiếp (`L1+L2+L3`)** | **70/85 (82.35%)** | **81/96 (84.38%)** | **38/39 (97.44%)** | **108 / 124 (87.10%)** |

---

## Phần D · Kiểm chứng độ phủ 8 chỉ số CBC, cơ chế gây vướng & số liệu quy mô chính thống

### 1. Độ phủ của 8 chỉ số CBC sản phẩm trên câu hỏi người dùng thật

Trong **`62 / 124` bài** có gọi trực tiếp tên chỉ số cụ thể (`52/85` BV Từ Dũ và `10/39` MEDLATEC — phần còn lại trên MEDLATEC gửi ảnh hoặc mã tra cứu bảng 18–32 chỉ số):
- **`59 / 62` (`95.16%`)** trên toàn tập đa nguồn — và **`51 / 52` (`98.08%`)** trên BV Từ Dũ — nhắc tới ít nhất 1 trong **đúng 8 chỉ số CBC của sản phẩm**.
- **Xếp hạng tần suất từng chỉ số trên `62` ca nêu tên:**
  1. `MCV`: **`34`** ca (`54.84%`) · 2. `HGB/Hb`: **`28`** ca (`45.16%`) · 3. `MCH`: **`25`** ca (`40.32%`) · 4. `HCT`: **`24`** ca (`38.71%`) · 5. `RBC`: **`23`** ca (`37.10%`) · 6. `PLT`: **`20`** ca (`32.26%`) · 7. `WBC`: **`19`** ca (`30.65%`) · 8. `MCHC`: **`16`** ca (`25.81%`).
  *(Mọi chỉ số phụ ngoài bộ 8 đều ít hơn hạng 8: `LYM = 14`, `RDW = 13`, `MPV/PDW = 12`, `NEU/GRAN = 11`, `MONO = 9`, `Ferritin/Fe = 6` — khẳng định bằng dữ liệu thật rằng lát cắt 8 chỉ số cốt lõi là lựa chọn tối ưu.)*
- **Cơ chế lặp lại trên `N = 124`:** `30/124 (24.19%)` nhắc tự tra mạng / sợ Thalassemia, ung thư máu, thiếu máu bất sản; `27/124 (21.77%)` tự chép tay `>= 3` mã viết tắt CBC vào câu hỏi; `23/124 (18.55%)` hỏi tên thuốc/liều viên sắt cụ thể (`Tohema, Safoli, Ferlatum, Saferon, Elevit, HemoQ mom, Obimin`); `15/124 (12.10%)` trộn lẫn đơn vị `g/L ↔ g/dL` hoặc `L/L ↔ %` (có phiếu viết nhầm `HCT 33.5 L/L`, `MCHC 37.3 g/L` ở `TD79`); `12/124 (9.68%)` nêu rõ dấu `gạch chân / bôi đậm / màu xanh-đỏ / CSBT`.

### 2. Số liệu dịch tễ & quy mô y tế công bố chính thức

- **Viện Dinh dưỡng Quốc gia — Bộ Y tế (Tổng điều tra Dinh dưỡng toàn quốc):** Tỷ lệ thiếu máu ở phụ nữ mang thai tại Việt Nam là **`25.6%`** (khu vực miền núi lên tới `~39%`), chủ yếu do thiếu sắt và acid folic — [viendinhduong.vn](https://viendinhduong.vn/vi/nutritional-issues/thieu-vi-chat-dinh-duong), [Viện Huyết học - Truyền máu TW](https://vienhuyethoc.vn/thieu-mau-o-phu-nu-mang-thai-hau-qua-kho-luong/).
- **Bệnh viện Từ Dũ (Báo cáo thống kê chính thức):** Tiếp nhận trung bình **`~1.000.000` lượt phụ nữ đến khám/năm** và đỡ sinh **`>60.000` ca sinh/năm** ([tudu.com.vn](https://www.tudu.com.vn/vn/gioi-thieu/lich-su-hinh-thanh/benh-vien-tu-du-nua-the-ky-vuon-minh-video/)), lịch khám thai chuẩn `8–12` lần/thai kỳ ([PDF Khám thai BV Từ Dũ](https://tudu.com.vn/cache/1548096_1.-Kh%C3%A1m-thai.pdf)).

### 3. ≥ 8 ví dụ & trích dẫn tiêu biểu (≤ 2 câu, ẩn danh PII, kèm nguồn)

1. **`TD36` (BV Từ Dũ, p120 · Thai 12w):** *"Những chỉ số nằm trong ngưỡng CSBT nhưng có một vài chỉ số vượt quá ngưỡng CSBT như em nêu ở dưới em chưa hiểu rõ như thế nào nhờ bác sĩ giải thích giúp em! ... WBC: 11.9 (CSBT: 4-10) ... 03 chỉ số trên ở phiếu kết quả của em bị gạch chân là như thế nào ạ?"* — [tudu.com.vn](https://tudu.com.vn/vn/suc-khoe-mang-thai/hoi-ve-ket-qua-xet-nghiem-mau-30394/) (xem 27/11/2026)
2. **`TD02` (BV Từ Dũ, p2 · Thai 16w):** *"nhưng đến ngày 3/10/2024 vợ em có thai khoảng 16 tuần thì xét nghiệm máu kết quả Hb 126 (108-164 g/L), MCV 78,8 (86,7-102,3 fL), MCH 26,2 (27,1-32,4 pg), MCHC 332 (297-331 g/L), HCT 0,379 (0,35-0,51 L/L) cho em hỏi kết quả như vậy có nguy cơ em bé sinh ra mắc bệnh thalassemia không vậy"* — [tudu.com.vn](https://tudu.com.vn/vn/suc-khoe-mang-thai/benh-thalassemia-46823/) (xem 27/11/2026)
3. **`TD45` (BV Từ Dũ, p150 · Thai 12w):** *"Bác sĩ khám trực tiếp nói em xét nghiệm xong không cần phải chờ lấy kết quả liền mà hôm khác lấy cũng được nên hôm nay khi nhận kết quả, em thấy có một vài chỉ số không nằm trong ngưỡng cho phép. Em mong bác sĩ giải thích giúp em: - Chỉ số Lym: 20.3% - Chỉ số MCV: 93.0fl..."* — [tudu.com.vn](https://tudu.com.vn/vn/suc-khoe-mang-thai/ket-qua-xet-nghiem-huyet-hoc-va-nuoc-tieu/) (xem 27/11/2026)
4. **`TD47` (BV Từ Dũ, p154 · Thai 12w):** *"Sau khi lấy kết quả xét nghiệm bác sĩ có xem qua nhưng chỉ quan tâm chủ yêu đến phần nguy cơ NTS và Rubella và cho biết kết quả là bình thường. Nhưng sau này coi lại kết quả xét nghiệm huyết học em thấy có một vài chỉ số không nằm trong mức cho phép."* — [tudu.com.vn](https://tudu.com.vn/vn/suc-khoe-mang-thai/ket-qua-xet-nghiem-mau-28353/) (xem 27/11/2026)
5. **`TD05` (BV Từ Dũ, p11 · Thai 34w2d):** *"Bác sĩ chỉ kết luận thiếu máu. Nhưng em tìm hiểu thì Mono giảm gợi ý đến thiếu máu bất sản. Vậy liệu kết quả xét nghiệm máu như trên thì em có bị thiếu máu bất sản khoogn ạ."* — [tudu.com.vn](https://tudu.com.vn/vn/suc-khoe-mang-thai/ket-qua-xet-nghiem-mau-45678/) (xem 27/11/2026)
6. **`ML19` (MEDLATEC Huyết học, p1 · Phiếu 32 chỉ số):** *"Xin bác sĩ đọc giúp tôi kết quả xét nghiệm ạ. có một vài chỉ số màu xanh, một số lại màu đen bôi đậm, có cả chỉ số màu đỏ nữa. tôi không biết có vấn đề gì không?"* — [medlatec.vn](https://medlatec.vn/hoi-dap/phan-tich-32-chi-so-tai-medlatec-c11541-q32999) (xem 27/11/2026)
7. **`ML37` (MEDLATEC Huyết học, p5 · Thai 22w):** *"E mang thai 22 tuần có làm xét nghiệm máu. Xin hỏi bác sỹ kết quả này của e cho thấy e bị thiếu máu đúng ko ạ? Bạch cầu tăng trong thai ky có nguy hiểm gì ko ạ."* — [medlatec.vn](https://medlatec.vn/hoi-dap/ket-qua-xet-nghiem-mau-c11541-q29431) (xem 27/11/2026)
8. **`ML23` (MEDLATEC Huyết học, p2 · Bảng tự chép):** *"chi so wbc la 13,6, chi so gran la 10,3, chi so gran(%g) la76,2, chi so pdw la17,9. bang xet nghem nay bac si ko giai thich gi e khong hieu lam ạ"* — [medlatec.vn](https://medlatec.vn/hoi-dap/xet-nghiem-c11541-q32378) (xem 27/11/2026)
9. **`TD79` (BV Từ Dũ, p252 · Thai 16w, in nhầm đơn vị trên phiếu):** *"WBC(Bạch cầu) : 16.2 G/L Bình thường : ( 4 - 10 G/L ) ... HCT(Hematocrite) : 33.5 L/L Bình thường : ( 35 - 54 L / L ) MCV : 79.3 fL ... MCHC : 37.3 g/L Bình thường : ( 32.0 - 36.0 g/L )"* — [tudu.com.vn](https://tudu.com.vn/vn/suc-khoe-mang-thai/ket-qua-xet-nghiem-huyet-hoc-truyen-mau/) (xem 27/11/2026)
10. **`RI0601` (BV Hùng Vương, *Pham et al., 2023*, TCN2 `21w3d`):** `HGB = 11.94 g/dL` (< `12.0 g/dL` ngưỡng nữ không mang thai) nhưng bình thường theo RI TCN2 (`9.71–13.17 g/dL`) và WHO 2024 (`>= 10.5 g/dL`); kèm ca `RI0114` ghi nhầm tuổi thai `12w7d`.

### 4. Giới hạn của dữ liệu
- **Giới hạn Phần A (*Pham et al., 2023*):** Workbook `.xlsx` gốc giữ ngoài repo công khai; chỉ phản ánh thai phụ đơn thai khỏe mạnh trên máy DxH 900 tại BV Hùng Vương, không đo trực tiếp cảm nhận hay số phút đọc phiếu.
- **Giới hạn Phần B & C (Hỏi – Đáp công khai BV Từ Dũ & MEDLATEC):** Người chủ động gửi câu hỏi trực tuyến là nhóm đã gặp vướng mắc hoặc có chỉ số lệch ngưỡng (`selection bias`), nên tỷ lệ `82.35%–97.44%` chỉ phản ánh cơ cấu đau trong nhóm tìm giải đáp, không phải tỷ lệ của toàn dân số mang thai; riêng MEDLATEC Huyết học gồm cả người khám tổng quát nên luôn được tách mẫu số riêng với tập thai kỳ `N_thai = 96`; ngoài ra dữ liệu Q&A không ghi trực tiếp số phút tự tra cứu tại nhà trước khi gửi hỏi (các thừa số thời gian & tần suất trong `spec.md` §2 giữ trung thực là `*(tự ước tính)*`).
