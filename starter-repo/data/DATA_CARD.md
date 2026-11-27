# Data card — dữ liệu bản chạy thử dùng

> Điền ở guide bước 2.4 (bản đầu ở CP2, đủ ở CP3). Ôn lại: ngày 6 · lab ngày 6. Chấm ở rubric R4.
> Không commit nguyên tài liệu khoá, dữ liệu cá nhân thật, ảnh phiếu thật hay file `.xlsx` gốc. Chỉ dùng số liệu tổng hợp, mã ẩn danh và dữ liệu `synthetic`.

## Dataset 1 · Dữ liệu CBC thai kỳ BV Hùng Vương (*Pham et al., 2023*) & 4 nguồn tham chiếu y khoa

| | |
|---|---|
| Dùng để làm gì | Nguồn đào bằng chứng pain (`evidence/data-mining.md`), bảng khoảng tham chiếu 8 chỉ số CBC theo TCN1/2/3 (`study` mode), ngưỡng lâm sàng WHO 2024, quy ước lịch khám BV Từ Dũ / MedlinePlus, và ví dụ ẩn danh (`RIxxxx`). Không thay thế khoảng tham chiếu trên phiếu của từng phòng xét nghiệm. |
| Từ đâu | Nghiên cứu cắt ngang *Pham et al. (2023)* tại Bệnh viện Hùng Vương, TP.HCM ([DOI: 10.1186/s12884-023-06106-2](https://doi.org/10.1186/s12884-023-06106-2), y đức `CS/HV/23/13`, `NCT05929326`); **WHO (2024)** ([9789240088542](https://www.who.int/publications/i/item/9789240088542)); **BV Từ Dũ** — *Khám thai* ([PDF](https://tudu.com.vn/cache/1548096_1.-Kh%C3%A1m-thai.pdf)); **MedlinePlus** ([Lab Results](https://medlineplus.gov/lab-tests/how-to-understand-your-lab-results/)). Workbook `.xlsx` gốc (`Huong_dan`, `Du_lieu`, `Tu_dien`) giữ **ngoài repo công khai**. |
| Xử lý những bước gì | Tuyển 879 thai phụ đơn thai khỏe mạnh → loại 12 lỗi kỹ thuật còn 867 bản ghi (`RI0001`–`RI0867`); lọc `cbc_panel_complete == 1` còn **837 panel CBC đủ** (máy Beckman Coulter DxH 900, K2EDTA); giữ tuần 28 trong TCN2 (`14w0d–28w6d`) theo BV Từ Dũ; loại ngoại lai Dixon `D/R >= 1/3` (CLSI EP28-A3c, **0 ca bị loại** trên 8 chỉ số chọn); tính phân vị 2.5th–97.5th (`R type 6`); chỉ trích số tổng hợp và mã ẩn danh (`RIxxxx`, `Pxxxx`), không chứa PII. |
| Số dòng / số đoạn | `867` bản ghi gốc (`305` TCN1 / `276` TCN2 / `286` TCN3) → **`837` panel CBC đủ** (`287` TCN1 / `273` TCN2 / `277` TCN3) và `836` panel đông máu; trích xuất 24 khoảng tham chiếu (8 chỉ số × 3 TCN) và các tỷ lệ kiểm chứng (`416/837 = 49.70%`, `95/837 = 11.35%`). |
| Phiên bản / ngày lấy | *Pham et al.* (dữ liệu 06–08/2023); *WHO* (2024); tổng hợp vào repo ngày 27/11/2026 (`evidence/data-mining.md`, `docs/n1-handoff.md`). |
| Nhãn | `thật` (số liệu tổng hợp từ nghiên cứu công bố; tệp `.xlsx` gốc không lưu trong repo công khai). |
| Giới hạn | Chỉ đại diện thai phụ đơn thai khỏe mạnh tại TP.HCM (mẫu tĩnh mạch trên máy DxH 900; *Pham et al.* Table 4 cho thấy RI không chuyển giao trực tiếp sang máy khác như Sysmex XE-2100); gồm 2 cặp trùng kỹ thuật (`P0613`, `P0798`), 1 cặp theo dõi dọc (`P0756`), 3 dị thường tuổi thai (`12w7d`, `1w2d`); không chứa dữ liệu hành vi/cảm nhận khi bệnh nhân tự đọc phiếu. |

## Dataset 2 · Bộ phiếu xét nghiệm CBC giả lập (3 ảnh PNG + 3 JSON đáp án) & JSON mẫu

| | |
|---|---|
| Dùng để làm gì | Đầu vào kiểm thử đọc/hiển thị phiếu và JSON đáp án cho N2 (`codebase/`) và N4 (UI/demo); **không dùng làm bằng chứng pain**. |
| Từ đâu | Nhóm tự sinh (`synthetic`) trong `starter-repo/data/` tương thích cấu trúc `data/cbc-demo-input.json` và danh mục `SUPPORTED_ANALYTES` (`codebase/references.py`): `cbc-mock-01-tcn1-normal.{png,json}` (`10w4d`), `cbc-mock-02-tcn2-borderline-unitmix.{png,json}` (`24w2d`, trộn đơn vị `g/L` vs `g/dL`), `cbc-mock-03-tcn3-microcytic-plt.{png,json}` (`33w1d`, `MCV/MCH` thấp + `PLT` giảm nhẹ). |
| Xử lý những bước gì | Dựng HTML phiếu bệnh viện gắn banner/watermark rõ ràng `"MẪU GIẢ LẬP (SYNTHETIC) — KHÔNG PHẢI PHIẾU XÉT NGHIỆM THẬT"`, kết xuất PNG độ phân giải cao (`2160×1880` px) bằng trình duyệt headless, và đối chiếu khớp 100% giá trị, đơn vị, khoảng tham chiếu và tuổi thai sang từng file JSON. |
| Số dòng / số đoạn | 3 ảnh PNG + 3 JSON đáp án (mỗi phiếu phủ đủ 8 chỉ số hỗ trợ giải thích `RBC, HGB, HCT, MCV, MCH, MCHC, WBC, PLT` = 24 dòng chỉ số giả lập), kèm `data/cbc-demo-input.json` (3 chỉ số) và `data/full-panel-demo.json` (24 chỉ số danh mục nền). |
| Phiên bản / ngày lấy | v1.1 · 27/11/2026 (đã đồng bộ 8 mã chuẩn `SUPPORTED_ANALYTES` trên `main`). |
| Nhãn | `synthetic` (dữ liệu giả lập 100%, không phải phiếu bệnh nhân thật). |
| Giới hạn | Sinh tất định từ 3 kịch bản lâm sàng cố định (không dùng ngẫu nhiên; thông số sinh học nhất quán `MCV ≈ HCT×10/RBC`, `MCH ≈ HGB×10/RBC`, `MCHC ≈ HGB×100/HCT`); người kiểm: Đào Ngọc Hân (N1); số dòng đã kiểm tay & script: 24/24 dòng chỉ số trên 3 cặp phiếu. Ca dựng sẵn để kiểm kỹ thuật, không đại diện tần suất hay trải nghiệm bệnh nhân thật. |

## Dataset 3 · Bộ câu thử Benchmark N3 (`eval/benchmark.csv`) & Câu ứng viên từ dữ liệu thật (`eval/n1-candidate-cases.csv`)

| | |
|---|---|
| Dùng để làm gì | `eval/benchmark.csv` dùng đánh giá hành vi giải thích 8 chỉ số, đối chiếu số học và an toàn ở lượt 1 (`run-1`); `eval/n1-candidate-cases.csv` lưu các ca ứng viên từ dữ liệu nghiên cứu & Q&A thật để mở rộng kiểm thử khi cần mà không làm lệch mốc lượt 1. |
| Từ đâu | `benchmark.csv`: 8 định nghĩa chỉ số do người dùng cung cấp (`B01–B08`, `data_that`) + 16 tình huống N3 tự viết (`B09–B24`, `tu_viet`). `n1-candidate-cases.csv`: **15 ca ứng viên (`N1_C01–N1_C15`)**, gồm `6` ca từ dữ liệu thật (`RI0601`, `RI0114`, `TD36`, `TD02`, `ML14`, `TD08`, `TD01` — thực tế `7` ca `data_that` gồm 1 từ BV Hùng Vương `RI0601`, 1 từ `RI0114`, 4 từ BV Từ Dũ và 1 từ MEDLATEC), `3` ca từ 3 phiếu giả lập `synthetic`, và `5` ca tấn công/biên `tu_viet`. |
| Xử lý / số dòng | `eval/benchmark.csv`: 24 payload JSON tổng hợp (`8` thường, `14` khó, `2` từ chối; `8/24 = 33.3%` `data_that`). `eval/n1-candidate-cases.csv`: 15 payload JSON chuẩn hóa schema `compare_cbc` đã ẩn danh PII hoàn toàn. |
| Nhãn | `benchmark.csv`: fixture tổng hợp giữ cố định sau CP2; `n1-candidate-cases.csv`: kết hợp `data_that` ẩn danh, `sinh_seed` và `tu_viet`. |
| Giới hạn | Khoảng trong `benchmark.csv` dùng kiểm logic đối chiếu (chưa bật hết chế độ `study`); chưa gộp thêm ca phỏng vấn trực tiếp `P1–P3` vì đang giữ `n = 0`. |

## Dataset 4 · Kho Hỏi – Đáp công khai đa nguồn BV Từ Dũ (`tudu.com.vn`) & MEDLATEC (`medlatec.vn`)

| | |
|---|---|
| Dùng để làm gì | Nguồn bằng chứng pain người dùng thật xuyên suốt 2 hệ thống y tế lớn (`evidence/data-mining.md` Phần B–C, `evidence/public-qa-cbc-table.md`, `evidence/summary.md`) kiểm chéo với dữ liệu lâm sàng BV Hùng Vương (`N = 837`) và chứng minh độ phủ 8 chỉ số CBC sản phẩm (`59/62 = 95.16%`). |
| Từ đâu | (1) Chuyên mục *Hỏi & đáp → Sức khỏe mang thai* công khai của Bệnh viện Từ Dũ (`https://tudu.com.vn/vn/suc-khoe-mang-thai/`); (2) Hai chuyên mục công khai *Sản phụ khoa* (`san-phu-khoa-c11534`) và *Huyết học* (`huyet-hoc-c11541`) của Hệ thống Y tế MEDLATEC (`https://medlatec.vn/hoi-dap`), cùng truy cập ngày `27/11/2026`. |
| Xử lý những bước gì | Chạy `evidence/mine_public_qa.py` quét tuần tự `300` trang BV Từ Dũ (`M = 3.586`) và trọn bộ `53 + 6` trang MEDLATEC (`M = 529 + 51 = 580`), xóa thẻ tên người hỏi (`faq-item-author`) trước khi trích văn bản, ẩn toàn bộ mã hồ sơ/SĐT `>= 7` chữ số thành `[mã XN]`, ẩn mật khẩu tra cứu và ẩn link chứa mã hồ sơ; tách phần câu hỏi, lọc bỏ nhiễu không phải CBC (`beta-hCG`, nước tiểu, soi tươi phụ khoa, 75g đường, Rubella, HIV, VGB), chỉ trích tối đa `≤ 2` câu/bài và tách mẫu số tập thai kỳ (`N_thai = 96`) khỏi tập đọc phiếu điện tử chung (`28`). |
| Số dòng / số đoạn | Quét `M_total = 4.166` bài liên tiếp → **`N_total = 124` bài CBC hợp lệ** (`85` BV Từ Dũ `TD01–TD85` + `39` MEDLATEC `ML01–ML39`), gắn 4 nhãn loại trừ lẫn nhau (`L1: 50/124`, `L2: 27/124`, `L3: 31/124`, `L4: 16/124`) và kiểm 0 vi phạm PII qua `--verify`. |
| Phiên bản / ngày lấy | Truy cập ngày `27/11/2026` (bài trong mẫu trải từ `2015` đến `10/2024`). |
| Nhãn | `thật` (dữ liệu hỏi đáp công khai đã ẩn danh PII, không lưu HTML toàn văn). |
| Giới hạn | Người gửi câu hỏi trực tuyến là nhóm có sẵn lo lắng hoặc lệch chỉ số (`selection bias`) nên tỷ lệ pain (`87.10%` toàn tập / `84.38%` tập thai kỳ) phản ánh cơ cấu vướng mắc của người cần giải đáp chứ không đại diện toàn dân số; không chứa số phút người dùng mất trước khi hỏi. |

## Dataset 5 · Số liệu dịch tễ & quy mô bệnh viện công bố chính thức

| | |
|---|---|
| Dùng để làm gì | Neo khung quy mô thực tế cho `spec.md §0, §2` và đối chiếu bối cảnh triển khai trong `cost/cost-estimate.md`. |
| Từ đâu | **Viện Dinh dưỡng Quốc gia — Bộ Y tế** (Tổng điều tra Dinh dưỡng toàn quốc, trích qua [viendinhduong.vn](https://viendinhduong.vn/vi/nutritional-issues/thieu-vi-chat-dinh-duong) và [Viện Huyết học - Truyền máu TW](https://vienhuyethoc.vn/thieu-mau-o-phu-nu-mang-thai-hau-qua-kho-luong/)); **Bệnh viện Từ Dũ** ([Báo cáo giới thiệu chính thức](https://www.tudu.com.vn/vn/gioi-thieu/lich-su-hinh-thanh/benh-vien-tu-du-nua-the-ky-vuon-minh-video/) và [Tài liệu Khám thai](https://tudu.com.vn/cache/1548096_1.-Kh%C3%A1m-thai.pdf)). |
| Số liệu đã trích | Tỷ lệ thiếu máu ở phụ nữ mang thai Việt Nam **`25.6%`** (`~39%` miền núi); riêng Bệnh viện Từ Dũ tiếp nhận **`~1.000.000` lượt phụ nữ khám/năm**, **`>60.000` ca sinh/năm**, lịch khám thai chuẩn `8–12` lần/thai kỳ. |
| Phiên bản / ngày lấy | Truy cập & kiểm tra nguồn ngày `27/11/2026`. |
| Nhãn | `thật` (số liệu công bố chính thức của cơ quan y tế và bệnh viện công lập). |
| Giới hạn | Là thống kê tổng hợp cấp quốc gia và bệnh viện, không đo trực tiếp hành vi đọc phiếu CBC tại nhà (các thừa số phút & tần suất sử dụng ở `spec.md §2` vẫn giữ nhãn `*(tự ước tính)*`). |

## Quy tắc ẩn danh & Không PII (Áp dụng toàn bộ dự án)
- **Tuyệt đối không thu thập hoặc lưu trong repo:** ảnh chụp phiếu xét nghiệm thật, họ tên, SĐT, email, CCCD, mã bệnh nhân, tên bác sĩ hoặc danh tính cơ sở gắn với người trả lời.
- **Mọi dữ liệu phỏng vấn (`P1`–`P3`) và trích xuất dữ liệu (`RIxxxx`)** dùng mã ẩn danh và giá trị tổng hợp/giả lập không truy vết được danh tính cá nhân; không tự tạo nội dung trích dẫn hay số liệu còn đang chờ thu thập.
