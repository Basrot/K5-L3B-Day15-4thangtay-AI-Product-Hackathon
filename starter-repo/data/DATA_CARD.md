# Data card — dữ liệu bản chạy thử dùng

> Điền ở guide bước 2.4 (bản đầu ở CP2, đủ ở CP3). Ôn lại: ngày 6 · lab ngày 6. Chấm ở rubric R4.
> Một trang. Mỗi dataset một mục. Dữ liệu chạy thử (phiếu giả lập, JSON đáp án…) để trong thư mục `data/` này.
> Không commit nguyên tài liệu khoá, dữ liệu cá nhân thật, ảnh phiếu thật hay file `.xlsx` gốc — chỉ trích đoạn tổng hợp, mã ẩn danh và dữ liệu `synthetic`.

## Dataset 1 · Dữ liệu CBC thai kỳ BV Hùng Vương (*Pham et al., 2023*) & 4 nguồn tham chiếu y khoa

| | |
|---|---|
| Dùng để làm gì | Nguồn đào bằng chứng pain (`evidence/data-mining.md`), bảng khoảng tham chiếu 8 chỉ số CBC theo TCN1/2/3, ngưỡng lâm sàng WHO 2024, quy ước lịch khám BV Từ Dũ / MedlinePlus, và trích xuất ca ẩn danh (`data_that`) cho bộ câu thử. |
| Từ đâu | Nghiên cứu cắt ngang *Pham et al. (2023)* tại Bệnh viện Hùng Vương, TP.HCM ([DOI: 10.1186/s12884-023-06106-2](https://doi.org/10.1186/s12884-023-06106-2), y đức `CS/HV/23/13`, `NCT05929326`); **WHO (2024)** ([9789240088542](https://www.who.int/publications/i/item/9789240088542)); **BV Từ Dũ** — *Khám thai* ([PDF](https://tudu.com.vn/cache/1548096_1.-Kh%C3%A1m-thai.pdf)); **MedlinePlus** ([Lab Results](https://medlineplus.gov/lab-tests/how-to-understand-your-lab-results/)). Workbook `.xlsx` gốc (`Huong_dan`, `Du_lieu`, `Tu_dien`) giữ **ngoài repo công khai**. |
| Xử lý những bước gì | Tuyển 879 thai phụ đơn thai khỏe mạnh → loại 12 lỗi kỹ thuật còn 867 bản ghi (`RI0001`–`RI0867`); lọc `cbc_panel_complete == 1` còn **837 panel CBC đủ** (máy Beckman Coulter DxH 900, K2EDTA); giữ tuần 28 trong TCN2 (`14w0d–28w6d`) theo BV Từ Dũ; loại ngoại lai Dixon `D/R >= 1/3` (CLSI EP28-A3c, **0 ca bị loại** trên 8 chỉ số chọn); tính phân vị 2.5th–97.5th (`R type 6`); chỉ trích số tổng hợp và mã ẩn danh (`RIxxxx`, `Pxxxx`), không chứa PII. |
| Số dòng / số đoạn | `867` bản ghi gốc (`305` TCN1 / `276` TCN2 / `286` TCN3) → **`837` panel CBC đủ** (`287` TCN1 / `273` TCN2 / `277` TCN3); trích xuất 24 khoảng tham chiếu (8 chỉ số × 3 TCN) và các tỷ lệ kiểm chứng (`416/837 = 49.70%`, `95/837 = 11.35%`). |
| Phiên bản / ngày lấy | *Pham et al.* (dữ liệu 06–08/2023); *WHO* (2024); tổng hợp vào repo ngày 27/11/2026 (`docs/NGHIEN_CUU_VA_DE_XUAT_DE_TAI_TRACK_B.md`). |
| Nhãn | `thật` (số liệu tổng hợp từ nghiên cứu công bố; tệp `.xlsx` gốc không lưu trong repo công khai). |
| Giới hạn | Chỉ đại diện thai phụ đơn thai khỏe mạnh tại TP.HCM (mẫu tĩnh mạch trên máy DxH 900; *Pham et al.* Table 4 cho thấy RI không chuyển giao trực tiếp sang máy khác như Sysmex XE-2100); gồm 2 cặp trùng kỹ thuật (`P0613`, `P0798`), 1 cặp theo dõi dọc (`P0756`), 3 dị thường tuổi thai (`12w7d`, `1w2d`); không chứa dữ liệu hành vi/cảm nhận khi bệnh nhân tự đọc phiếu. |

## Dataset 2 · Bộ phiếu xét nghiệm CBC giả lập (3 ảnh PNG + 3 JSON đáp án) & JSON mẫu

| | |
|---|---|
| Dùng để làm gì | Đầu vào kiểm thử đọc/hiển thị phiếu và JSON đáp án cho N2 (`codebase/`) và N4 (UI/demo); **không dùng làm bằng chứng pain**. |
| Từ đâu | Nhóm tự sinh (`synthetic`) trong `starter-repo/data/` tương thích cấu trúc `data/cbc-demo-input.json`: `cbc-mock-01-tcn1-normal.{png,json}` (`10w4d`), `cbc-mock-02-tcn2-borderline-unitmix.{png,json}` (`24w2d`, trộn đơn vị `g/L` vs `g/dL`), `cbc-mock-03-tcn3-microcytic-plt.{png,json}` (`33w1d`, `MCV/MCH` thấp + `PLT` giảm nhẹ). |
| Xử lý những bước gì | Dựng HTML phiếu bệnh viện gắn banner/watermark rõ ràng `"MẪU GIẢ LẬP (SYNTHETIC) — KHÔNG PHẢI PHIẾU XÉT NGHIỆM THẬT"`, kết xuất PNG độ phân giải cao bằng trình duyệt headless, và đối chiếu khớp 100% giá trị, đơn vị, khoảng tham chiếu và tuổi thai sang từng file JSON. |
| Số dòng / số đoạn | 3 ảnh PNG + 3 JSON đáp án (mỗi phiếu phủ đủ 8 chỉ số `RBC, HGB, HCT, MCV, MCH, WBC, NEUT_abs, PLT` = 24 dòng chỉ số giả lập), kèm 1 file mẫu gốc `data/cbc-demo-input.json` (3 chỉ số). |
| Phiên bản / ngày lấy | v1.0 · 27/11/2026. |
| Nhãn | `synthetic` (dữ liệu giả lập 100%, không phải phiếu bệnh nhân thật). |
| Giới hạn | **Data `synthetic` (nhóm tự sinh):** Sinh tất định từ 3 kịch bản lâm sàng cố định (không dùng ngẫu nhiên; thông số tham chiếu lấy từ bảng *Pham et al. 2023* và ngưỡng WHO 2024); người kiểm: Đào Ngọc Hân (N1); số dòng đã kiểm tay & script: 24/24 dòng chỉ số trên 3 cặp phiếu (khớp 100% PNG ↔ JSON). Data tự dựng **không phải bằng chứng pain**. **Lưu ý đồng bộ N2/N4:** `codebase/tools.py` và `spec.md §4` hiện chỉ kiểm tra 3 chỉ số (`HGB`, `WBC`, `PLT`), trong khi 3 bộ phiếu giả lập phủ đủ 8 chỉ số theo phạm vi đề tài (`RBC, HGB, HCT, MCV, MCH, WBC, NEUT_abs, PLT`) — N2 có thể lọc tập con 3 chỉ số cho bản CP2 hoặc mở rộng `tools.py` lên 8 chỉ số. |

## Quy tắc ẩn danh & Không PII (Áp dụng toàn bộ dự án)
- **Tuyệt đối không thu thập hoặc lưu trong repo:** ảnh chụp phiếu xét nghiệm thật, họ tên, SĐT, email, CCCD, mã bệnh nhân, tên phòng khám gắn danh tính cá nhân.
- **Mọi dữ liệu phỏng vấn (`P1`–`P3`) và ứng viên benchmark (`eval/n1-candidate-cases.csv`)** dùng mã ẩn danh (`P1..P3`, `RIxxxx`) và giá trị tổng hợp/giả lập không truy vết được danh tính cá nhân.
