# Tổng hợp bằng chứng pain (4 trụ cột đa nguồn)

> Điền ở guide bước 1.2, xong trước **CP3 10:00 Thứ Bảy 28/11**. Chấm ở rubric R1.
> **Nguyên tắc trung thực:** Không bịa phỏng vấn hay trích dẫn; mọi số liệu chưa thu từ phỏng vấn trực tiếp đều giữ rõ trạng thái thật và ghi `*(tự ước tính)*` ở bảng Impact.

## 1. Nguồn đã dùng

| Nguồn | Đạt ngưỡng? | Quy mô / Kết quả chính | File |
|---|---|---|---|
| **Nguồn 1 · Dữ liệu lâm sàng BV Hùng Vương (*Pham et al., 2023*)** | ☑ Đạt (`N = 837`) | **`416/837 (49.70%)`** thai phụ khỏe có `HGB < 12.0 g/dL` (bị gắn cờ sai nếu dùng ngưỡng nữ không mang thai); `95/837 (11.35%)` dưới WHO 2024 | `evidence/data-mining.md` (Phần A) |
| **Nguồn 2 · Hỏi – Đáp thai kỳ công khai BV Từ Dũ (`tudu.com.vn`, 300 trang)** | ☑ Đạt (`N = 85` từ `M = 3.586`) | **`70/85 (82.35%)`** xoay quanh lo lệch ngưỡng (`40.00%`), lúng túng mã/đơn vị (`11.76%`), hỏi uống/tăng liều sắt (`30.59%`); **`51/52 (98.08%)`** ca nêu tên chỉ số nằm trong bộ 8 CBC | `evidence/data-mining.md` (Phần B), `evidence/public-qa-cbc-table.md` |
| **Nguồn 3 · Hỏi – Đáp Xét nghiệm & Sản phụ khoa MEDLATEC (`medlatec.vn`, 59 trang)** | ☑ Đạt (`N = 39` từ `M = 580`) | **`38/39 (97.44%)`** vướng đọc hiểu/lo lắng khi nhận phiếu trả qua cổng điện tử/SMS (`43.59%` lúng túng mã, màu sắc xanh/đỏ/đen đậm, bảng 18–32 chỉ số) | `evidence/data-mining.md` (Phần C), `evidence/public-qa-cbc-table.md` |
| **Nguồn 4 · Số liệu dịch tễ & quy mô chính thống (Viện Dinh dưỡng / Bộ Y tế & BV Từ Dũ)** | ☑ Đạt (tham chiếu vĩ mô) | **`25.6%`** thai phụ Việt Nam thiếu máu (Tổng điều tra Dinh dưỡng QG); riêng BV Từ Dũ **`~1.000.000` lượt khám** và **`>60.000` ca sinh/năm** | `evidence/data-mining.md` (Phần D.2), `spec.md` §2 |
| **Nguồn 5 · Phỏng vấn trực tiếp (`≥3` người ngoài nhóm)** | ☐ Chưa thực hiện (`n = 0`) | Giữ trung thực chưa phỏng vấn; các thừa số phút/tần suất ở `spec.md §2` ghi `*(tự ước tính)*` | `evidence/interviews/PLAN.md`, `P1.md`–`P3.md` |
| **Nguồn 6 · Khảo sát** | ☐ Không sử dụng (`n = 0`) | — | `evidence/survey/` |

## 2. Tổng hợp số chính (cập nhật 27/11/2026)

- **Dữ liệu lâm sàng BV Hùng Vương (*Pham et al., 2023*, `N = 837`):**
  - **`416/837 (49.70%)`** thai phụ khỏe mạnh có `HGB < 12.0 g/dL` (bị gắn cờ thiếu máu sai theo ngưỡng nữ không mang thai WHO 2024); **`95/837 (11.35%)`** dưới ngưỡng sàng lọc thai kỳ WHO 2024 (`TCN1 7.67%`, `TCN2 10.26%`, `TCN3 16.25%`); `WBC` sinh lý thai kỳ lên tới `14.14–15.55 × 10^9/L`.
- **Dữ liệu Hỏi – Đáp thật đa nguồn (`M_total = 4.166` bài quét → `N_total = 124` bài sạch PII):**
  - **`108/124 (87.10%)`** xoay quanh 3 nhóm đau trực tiếp (`L1` lo lệch ngưỡng/bệnh nặng `50/124 = 40.32%`; `L2` lúng túng mã/đơn vị/màu sắc/bảng 18–32 chỉ số `27/124 = 21.77%`; `L3` hỏi uống/tăng giảm liều sắt `31/124 = 25.00%`).
  - **Tách riêng tập thai kỳ / tiền sản thuần túy (`N_thai = 96`: `85` Từ Dũ + `11` MEDLATEC):** **`81/96 (84.38%)`** thuộc nhóm `L1 + L2 + L3` (`L1: 40.62%`, `L2: 12.50%`, `L3: 31.25%`).
  - **Chứng minh độ phủ 8 chỉ số CBC cốt lõi:** Trong **`62/124`** ca nêu tên chỉ số cụ thể, **`59/62 (95.16%)`** toàn tập — và **`51/52 (98.08%)`** trên BV Từ Dũ — thuộc đúng 8 mã sản phẩm (`MCV=34, HGB=28, MCH=25, HCT=24, RBC=23, PLT=20, WBC=19, MCHC=16`; cao hơn tất cả chỉ số phụ `LYM=14, RDW=13, MPV/PDW=12, NEU=11, MONO=9, Ferritin=6`).
- **Quy mô thực tế được neo bởi thống kê Bộ Y tế / BV Từ Dũ:** Tỷ lệ thiếu máu thai kỳ toàn quốc **`25.6%`** (*Viện Dinh dưỡng*); riêng BV Từ Dũ có **`>60.000` ca sinh/năm** và **`~1.000.000` lượt khám/năm** (`8–12` lần/thai kỳ).

## 3. ≥ 8 trích dẫn nguyên văn tiêu biểu xuyên suốt 3 nguồn (≤ 2 câu, đã ẩn danh PII)

1. **`[BV Từ Dũ · TD36 · Thai 12w]`** *"Những chỉ số nằm trong ngưỡng CSBT nhưng có một vài chỉ số vượt quá ngưỡng CSBT như em nêu ở dưới em chưa hiểu rõ như thế nào nhờ bác sĩ giải thích giúp em! ... WBC: 11.9 (CSBT: 4-10) ... 03 chỉ số trên ở phiếu kết quả của em bị gạch chân là như thế nào ạ?"* — [tudu.com.vn](https://tudu.com.vn/vn/suc-khoe-mang-thai/hoi-ve-ket-qua-xet-nghiem-mau-30394/) (xem 27/11/2026)
2. **`[BV Từ Dũ · TD02 · Thai 16w]`** *"nhưng đến ngày 3/10/2024 vợ em có thai khoảng 16 tuần thì xét nghiệm máu kết quả Hb 126 (108-164 g/L), MCV 78,8 (86,7-102,3 fL), MCH 26,2 (27,1-32,4 pg), MCHC 332 (297-331 g/L), HCT 0,379 (0,35-0,51 L/L) cho em hỏi kết quả như vậy có nguy cơ em bé sinh ra mắc bệnh thalassemia không vậy"* — [tudu.com.vn](https://tudu.com.vn/vn/suc-khoe-mang-thai/benh-thalassemia-46823/) (xem 27/11/2026)
3. **`[MEDLATEC Huyết học · ML37 · Thai 22w]`** *"E mang thai 22 tuần có làm xét nghiệm máu. Xin hỏi bác sỹ kết quả này của e cho thấy e bị thiếu máu đúng ko ạ? Bạch cầu tăng trong thai ky có nguy hiểm gì ko ạ."* — [medlatec.vn](https://medlatec.vn/hoi-dap/ket-qua-xet-nghiem-mau-c11541-q29431) (xem 27/11/2026)
4. **`[MEDLATEC Huyết học · ML19 · Phiếu 32 chỉ số]`** *"Xin bác sĩ đọc giúp tôi kết quả xét nghiệm ạ. có một vài chỉ số màu xanh, một số lại màu đen bôi đậm, có cả chỉ số màu đỏ nữa. tôi không biết có vấn đề gì không?"* — [medlatec.vn](https://medlatec.vn/hoi-dap/phan-tich-32-chi-so-tai-medlatec-c11541-q32999) (xem 27/11/2026)
5. **`[BV Từ Dũ · TD47 · Thai 12w]`** *"Sau khi lấy kết quả xét nghiệm bác sĩ có xem qua nhưng chỉ quan tâm chủ yêu đến phần nguy cơ NTS và Rubella và cho biết kết quả là bình thường. Nhưng sau này coi lại kết quả xét nghiệm huyết học em thấy có một vài chỉ số không nằm trong mức cho phép."* — [tudu.com.vn](https://tudu.com.vn/vn/suc-khoe-mang-thai/ket-qua-xet-nghiem-mau-28353/) (xem 27/11/2026)
6. **`[BV Từ Dũ · TD05 · Thai 34w2d]`** *"Bác sĩ chỉ kết luận thiếu máu. Nhưng em tìm hiểu thì Mono giảm gợi ý đến thiếu máu bất sản. Vậy liệu kết quả xét nghiệm máu như trên thì em có bị thiếu máu bất sản khoogn ạ."* — [tudu.com.vn](https://tudu.com.vn/vn/suc-khoe-mang-thai/ket-qua-xet-nghiem-mau-45678/) (xem 27/11/2026)
7. **`[BV Từ Dũ · TD08 · Thai 33w]`** *"Em có thai tuần 33, mỗi ngày có uống 1 ống sắt tohema nhưng dạo gần đây hay chóng mặt, xét nghiệm máu ko bị thiếu máu... Em muốn uống tăng lên 1 ngày 2 ống sắt dc ko ạ."* — [tudu.com.vn](https://tudu.com.vn/vn/suc-khoe-mang-thai/thuoc-sat-trong-thai-ky/) (xem 27/11/2026)
8. **`[BV Từ Dũ · TD79 · Thai 16w]`** *"WBC(Bạch cầu) : 16.2 G/L Bình thường : ( 4 - 10 G/L ) ... HCT(Hematocrite) : 33.5 L/L Bình thường : ( 35 - 54 L / L ) MCV : 79.3 fL ... MCHC : 37.3 g/L Bình thường : ( 32.0 - 36.0 g/L )"* — [tudu.com.vn](https://tudu.com.vn/vn/suc-khoe-mang-thai/ket-qua-xet-nghiem-huyet-hoc-truyen-mau/) (xem 27/11/2026)
9. **`[Dữ liệu BV Hùng Vương · RI0601 · TCN2 21w3d]`** `HGB = 11.94 g/dL` (< `12.0 g/dL` ngưỡng nữ không mang thai) nhưng bình thường theo RI TCN2 (`9.71–13.17 g/dL`) và WHO 2024 (`>= 10.5 g/dL`), cùng ca dị thường tuổi thai `RI0114` (`12w7d`) — `evidence/data-mining.md` (*Pham et al., 2023*).

## 4. Kiểm chéo giữa các nguồn (Triangulation)

- **Điểm khớp mạnh giữa dữ liệu lâm sàng (BV Hùng Vương) và tiếng nói bệnh nhân thật (BV Từ Dũ + MEDLATEC):**
  - **Bẫy ngưỡng người không mang thai:** Dữ liệu BV Hùng Vương cho thấy `49.70%` thai phụ khỏe có `HGB < 12.0 g/dL` và `WBC` sinh lý lên tới `15.55 × 10^9/L`. Bên ngoài thực tế, thai phụ tại cả BV Từ Dũ (`TD36`: `WBC 11.9` bị gạch chân so với `CSBT 4-10`; `TD75`: `Hb 12.2` thấp hơn `12.5-14.5`; `TD84`: `Hb 12.3` thấp hơn `12.5-14.5`) lẫn MEDLATEC (`ML37`: bầu 22w lo *"Bạch cầu tăng trong thai kỳ có nguy hiểm gì không"*) đều gặp chính xác hiện tượng bị gắn cờ/gạch chân/tô màu đỏ đen.
  - **Điểm đứt gãy ngay khi rời phòng khám:** Ở BV Từ Dũ, thai phụ về nhà đọc lại tờ xét nghiệm Double test/huyết học thấy `Lym`/`MCV`/`RBC` lệch khung (`TD45`, `TD47`, `TD75`); sang MEDLATEC, trả kết quả điện tử khiến nhóm câu hỏi lúng túng mã/màu sắc tăng vọt từ **`11.76%` lên `43.59%`**, thậm chí `ML03` / `ML19` / `ML23` nhấn mạnh *"tổng phân tích máu 32 chỉ số"*, *"màu xanh, đen bôi đậm, màu đỏ"*, *"bác sĩ không giải thích gì"*.
  - **Cổng chặn an toàn y tế & đổi đơn vị:** Có tới **`30.59%`** câu hỏi tại BV Từ Dũ hỏi trực tiếp về thuốc sắt (`TD08` đòi tăng gấp đôi Tohema), và **`12.10%`** toàn bộ 124 ca chép lẫn đơn vị `g/L ↔ g/dL` và `L/L ↔ %` (có cả phiếu in nhầm `33.5 L/L` và `37.3 g/L` ở `TD79`) — chứng minh thiết kế quy đổi tất định bằng Python `Decimal` (`compare_cbc`) và chặn cứng `medical_advice` là bắt buộc.

## 5. Kết luận

- **Giả thuyết ban đầu (`evidence/hypothesis.md`): ĐƯỢC XÁC NHẬN VỮNG CHẮC qua 4 trụ cột độc lập** (`N = 837` mẫu lab BV Hùng Vương, `N = 85` Q&A BV Từ Dũ, `N = 39` Q&A MEDLATEC, và thống kê dịch tễ Bộ Y tế / BV Từ Dũ).
- **Lát cắt 8 chỉ số CBC được chứng minh trực tiếp từ dữ liệu:** Bao phủ **`95.16%` (`59/62`)** toàn tập nêu tên chỉ số và **`98.08%` (`51/52`)** tại BV Từ Dũ.
- **Điểm còn thiếu trung thực:** `P1–P3` phỏng vấn trực tiếp (`0/3`) chưa thực hiện nên số phút tự tra cứu/phiên tại nhà trong `spec.md` §2 vẫn giữ nhãn `*(tự ước tính)*`.
