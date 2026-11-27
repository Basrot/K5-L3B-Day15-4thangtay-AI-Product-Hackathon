# Data card — dữ liệu bản chạy thử

> Không commit nguyên tài liệu khoá, dữ liệu cá nhân thật, ảnh phiếu thật hay file `.xlsx` gốc. Chỉ dùng số liệu tổng hợp, mã ẩn danh và dữ liệu `synthetic`.

## Dataset 1 · Nghiên cứu CBC thai kỳ Việt Nam (*Pham et al., 2023*)

| | |
|---|---|
| Dùng để làm gì | Nguồn tham khảo cho khoảng CBC theo tam cá nguyệt, kiểm chứng dữ liệu tổng hợp và ví dụ ẩn danh; không thay thế khoảng tham chiếu trên phiếu của từng phòng xét nghiệm. |
| Từ đâu | Nghiên cứu tại Bệnh viện Hùng Vương, TP.HCM ([DOI: 10.1186/s12884-023-06106-2](https://doi.org/10.1186/s12884-023-06106-2)). Workbook gốc được người dùng cung cấp nhưng giữ ngoài repo công khai. Nguồn hướng dẫn bổ sung: [WHO 2024](https://www.who.int/publications/i/item/9789240088542), [Bệnh viện Từ Dũ](https://tudu.com.vn/cache/1548096_1.-Kh%C3%A1m-thai.pdf), [MedlinePlus](https://medlineplus.gov/lab-tests/how-to-understand-your-lab-results/). |
| Xử lý những bước gì | Theo tài liệu N1: 879 thai phụ ban đầu, loại 12 lỗi kỹ thuật còn 867 bản ghi; giữ tuần 28 trong TCN2 (14w0d–28w6d); lọc panel CBC đủ còn 837. Chỉ ghi số liệu tổng hợp và mã ẩn danh, không đưa PII hoặc workbook gốc vào repo. |
| Số dòng / số đoạn | 867 bản ghi (305/276/286 theo TCN1/2/3), 837 panel CBC đủ (287/273/277). Tuổi thai dạng `21w3d`; 837 panel CBC và 836 panel đông máu đầy đủ theo file người dùng gửi. |
| Phiên bản / nhãn | Dữ liệu nghiên cứu công bố; workbook gốc ngoài repo. Thông tin mô tả/kiểm tra chi tiết: `evidence/data-mining.md` và `docs/n1-handoff.md`. |
| Giới hạn | Thai phụ đơn thai khỏe mạnh tại một bệnh viện, thiết bị và quần thể cụ thể; khoảng nghiên cứu không đồng nhất với khoảng lab hay ngưỡng chẩn đoán. Không chứa bằng chứng về trải nghiệm người dùng khi tự đọc phiếu. |

## Dataset 2 · Phiếu CBC giả lập và JSON đáp án

| | |
|---|---|
| Dùng để làm gì | Kiểm thử đọc/hiển thị phiếu và luồng UI; hỗ trợ N2/N4. Không dùng làm bằng chứng pain. |
| Từ đâu | Nhóm tự tạo: `cbc-mock-01-tcn1-normal`, `cbc-mock-02-tcn2-borderline-unitmix`, `cbc-mock-03-tcn3-microcytic-plt` (mỗi ca có PNG và JSON). |
| Xử lý những bước gì | Tạo phiếu có watermark “MẪU GIẢ LẬP — KHÔNG PHẢI PHIẾU XÉT NGHIỆM THẬT”; đối chiếu PNG với JSON. Ba phiếu phủ 8 mã `RBC, HGB, HCT, MCV, MCH, MCHC, WBC, PLT`. |
| Số dòng / nhãn | 3 ảnh PNG + 3 JSON, dữ liệu `synthetic`; người kiểm theo bàn giao N1 là Đào Ngọc Hân. |
| Giới hạn | Ca dựng sẵn để kiểm kỹ thuật, không đại diện tần suất hay trải nghiệm bệnh nhân thật. |

## Dataset 3 · Benchmark N3

| | |
|---|---|
| Dùng để làm gì | Đánh giá hành vi giải thích 8 chỉ số và đối chiếu với khoảng trong `eval/benchmark.csv`; không dùng để huấn luyện. |
| Từ đâu | 8 định nghĩa chỉ số do người dùng cung cấp, cộng 16 tình huống N3 tự viết. N1 có thêm `eval/n1-candidate-cases.csv`; các câu đó chưa được đưa vào benchmark chính ở lượt 1. |
| Xử lý / số dòng | 24 payload JSON tổng hợp: 8 thường, 14 khó, 2 từ chối. Không có hồ sơ bệnh nhân thật. |
| Nhãn | Fixture tổng hợp; 8 định nghĩa người dùng cung cấp không phải câu nói từ phỏng vấn. |
| Giới hạn | Khoảng trong fixture dùng kiểm logic, không phải khoảng lâm sàng. Benchmark chính chưa có 8 câu nói đã ẩn danh từ phỏng vấn người dùng cuối. |

## Quy tắc riêng tư

Không lưu ảnh phiếu xét nghiệm thật, họ tên, số điện thoại, email, CCCD, mã bệnh nhân hoặc danh tính cơ sở gắn với người trả lời. Phỏng vấn dùng mã `P1`–`P3`; không tự tạo nội dung trích dẫn hay số liệu còn đang chờ thu thập.
