# Đề bài — AI cho việc học và dạy ở chính khoá AI20K: 5 track, một khung chung

> [README](README.md) → **[01-challenge-brief]** → [tracks/](tracks/README.md) → [02-guide](02-guide.md) → [03-rubric](03-rubric.md)

**Bối cảnh.** Khoá AI20K khoá 5 đang chạy với hơn 1.000 học viên (L23 và L34). Những việc đang diễn ra hằng ngày trong khoá:
- Trước mỗi buổi, học viên học trên LMS và trang pre-class của khoá: xem video, trả lời câu hỏi giữa video, làm mini lab, hỏi trợ giảng AI, học cùng các bạn học AI.
- Học viên hỏi đáp trên Discord, nhận thông báo qua Discord, email và nhiều kênh khác, lên lớp với giảng viên và lab coach.
- Ban đào tạo xếp lịch, xếp phòng, chia việc cho giảng viên và lab coach.
- Giảng viên và đội sản xuất làm bài giảng video và bài tương tác bằng AI.

Ở mỗi chỗ đều có việc lặp lại, chỗ nghẽn, chỗ sai thì đắt.

**Nhóm là một product team làm AI.** Nhóm phải làm đủ ba việc:
1. Chọn một track và tìm một pain có bằng chứng.
2. Thiết kế giải pháp AI cho **một lát cắt**, cả về sản phẩm (ai dùng, dùng lúc nào, kết quả là gì) lẫn công nghệ (AI quyết định gì, dựa trên dữ liệu và công cụ nào, workflow hay agent, chặn rủi ro thế nào).
3. Chứng minh bằng số: giải pháp **đúng được bao nhiêu** trên bộ câu thử, và **tốn bao nhiêu mỗi tháng** khi đưa vào dùng thật.

---

## Chọn 1 track, rồi tìm bài toán của nhóm trong track

| Track | Bối cảnh | Định hướng ý tưởng | File |
|---|---|---|---|
| **A** · AI Tutor cho LMS và trang pre-class | Học viên học trước buổi trên LMS và trang pre-class. Trợ giảng AI ngay dưới video đã chạy thật với nhiều lượt hỏi | Làm việc học trước buổi hiệu quả hơn: trợ giảng trả lời có căn cứ hơn, hoặc một tính năng AI mới cho học viên, giảng viên | [track-a](tracks/track-a-tutor-lms-preclass.md) |
| **B** · Trợ lý Discord | Discord của khoá rất đông. Thông báo, hỏi bài, hỏi lịch, hạn nộp nằm rải rác, câu hỏi lặp lại nhiều, trả lời sai hạn là hậu quả trực tiếp | Giúp học viên tìm đúng thông tin chính thức. Giúp TA và lab coach không bỏ sót câu hỏi, thấy được lớp đang kẹt gì | [track-b](tracks/track-b-discord-assistant.md) |
| **C** · Sản xuất bài giảng bằng AI | Bài giảng online (video, bài tương tác) làm bằng AI. Model sinh kịch bản, slide, video đã tốt. Chỗ nghẽn chuyển sang **kiểm và duyệt**: nội dung có đúng không, lấy từ đâu, ai duyệt | Agent hỗ trợ trong quy trình làm bài giảng: tìm và trích nguồn, rà soát kiến thức, biến bài giảng thành bài tương tác, sửa theo góp ý người học. Hoặc ý tưởng riêng của nhóm | [track-c](tracks/track-c-online-lesson-production.md) |
| **D** · Lớp học kiểu mới | Người học học nhiều hơn khi được tương tác và tự kiến tạo. AI làm được điều một giảng viên không làm nổi với hàng trăm người. Trang pre-class đã có một lớp học AI (trợ giảng AI + bạn học AI): đó chỉ là **một concept mẫu** | Trải nghiệm học khiến học viên chủ động hơn, hiểu sâu hơn, nhớ lâu hơn: điều phối, cá nhân hoá, học từ lỗi, học bằng cách dạy, game hoá… hoặc concept riêng | [track-d](tracks/track-d-new-classroom.md) |
| **E** · Làn mở | Những việc khác trong khoá. Ví dụ vận hành đào tạo: lịch, phòng, phân công. Khoá đang thiếu cơ sở vật chất, phòng thường chỉ chốt sát ngày | Một pain thật trong khoá mà A–D chưa chạm tới. Hướng nổi bật: **vận hành đào tạo**. Gợi ý khác: khách hàng ảo tập phỏng vấn · giám khảo ảo · hỗ trợ lab · chấm theo tiêu chí · ghép nhóm | [track-e](tracks/track-e-open-lane.md) |

- **Định hướng ý tưởng chỉ là điểm xuất phát, không phải danh sách đóng.** Nhóm được đi theo hướng khác, miễn là vẫn nằm trong bối cảnh của track và có pain có bằng chứng. Bài toán không thuộc track nào trong A–D thì chọn track E.
- Dù đi theo hướng gợi ý hay hướng riêng, nhóm vẫn **tự cắt lát cắt của mình** từ pain đã chứng minh.
- Mỗi file track viết theo cùng một khung để dễ so sánh: bối cảnh · người dùng · data · định hướng ý tưởng · công cụ gợi ý · persona chi phí · bẫy · an toàn. Cách chọn track trong 20 phút: [tracks/README.md](tracks/README.md).
- **Mọi track chấm chung một rubric** ([03-rubric.md](03-rubric.md)). Đi theo hướng riêng không bị chấm khác.

<a id="data"></a>
## Data

- **BTC cấp các bộ data chính** trong `data/` để đào bằng chứng và hình dung bối cảnh:
  - [data/preclass/](data/preclass/README.md): nhật ký hành vi thật của khoá trên trang pre-class, từ 05/11 đến 25/11/2026. Đã ẩn danh, mọi mã đã thay mới. Liên quan nhất tới track A và D.
  - [data/training-ops/](data/training-ops/README.md): bộ **giả lập** dựng lại cách khoá vận hành lịch học, xếp phòng, phân công giảng viên và lab coach (track B, E). Dùng để hình dung và chạy thử, **không phải bằng chứng pain**.
- **Data để chạy thử** (bài mẫu có mã đoạn, thông báo mẫu, đoạn transcript…) **nhóm tự dựng**: trích ngắn hoặc viết lại từ tài liệu khoá, hoặc tự sinh có seed. Ghi nguồn và cách dựng trong `data/DATA_CARD.md` ([guide 2.4](02-guide.md#b2-4)). Data tự dựng **không phải bằng chứng pain**.
- Với track A, B, D, **cả lớp là người dùng thật**: phỏng vấn hoặc khảo sát được ngay trong giờ nghỉ.

**Luật dùng dữ liệu**
1. **Người được phỏng vấn / khảo sát:** ghi P1, P2… kèm vai, không ghi họ tên, số điện thoại, email, mã học viên. Không ghi âm khi chưa được đồng ý.
2. **data/preclass/:** không cố đoán ai là ai, không xếp hạng học viên. Repo nhóm chỉ chứa số đã tổng hợp và vài dòng ví dụ, không chép lại nguyên file.
3. **Discord và bài công khai:** người trong đó là bạn cùng khoá. Trích tối đa 2 câu, bỏ tên, không đoán "tin này của ai".
4. **Tài liệu khoá** (slide, transcript, đề lab): repo nhóm là công khai, nên **không commit nguyên tài liệu**, chỉ trích đoạn ngắn.
5. **Công cụ AI gói miễn phí** có thể dùng dữ liệu gửi lên để huấn luyện.
   - Data trong `data/` của bộ đề **được đưa vào thoải mái**: đã ẩn danh hoặc là giả lập.
   - Dữ liệu người thật nhóm tự thu (phỏng vấn, khảo sát, Discord) chỉ đưa bản đã bỏ tên hoặc đoạn đã viết lại.

## Lát cắt = MỘT CÂU

> **một người dùng · một công việc · một quyết định AI · một kết quả**

Ví dụ để hình dung độ lớn: *Một học viên · dán lỗi khi làm lab · AI quyết định gợi ý bước tiếp theo mà không đưa lời giải · học viên tự sửa được.*

- Lát cắt **phải đi ra từ pain đã chứng minh**, không đi ra từ ý tưởng ban đầu.
- Demo được trong 2 phút, làm trọn trong khoảng 10 giờ. Bối cảnh càng lớn (C, D) thì lát cắt càng phải nhỏ.
- Viết ở Canvas dòng 5 ([guide 1.4](02-guide.md#b1-4)) và `spec.md` §4.

## Ràng buộc chung

1. **Phạm vi: chỉ việc học và dạy ở chính khoá AI20K.** Người dùng phải là người trong khoá (học viên, giảng viên, TA, lab coach, ban đào tạo, đội sản xuất) mà nhóm gặp được trong hai ngày.
2. **Bản chạy thử chạy riêng, không sửa hệ thống thật của khoá** (trang pre-class, LMS, Discord).
   - Đó là bản mô phỏng tính năng (dòng lệnh, web nhỏ, bot thử, notebook) trên dữ liệu giả lập, tự viết hoặc đã ẩn danh. Không bắt buộc đưa lên mạng.
   - Bắt buộc: gọi AI thật ở quyết định trung tâm, và quyết định dựa trên dữ liệu / công cụ của bài toán ([guide 3.2](02-guide.md#b3-2)).
3. **Tự xác định 4 lớp chỗ khó** cho lát cắt, rồi biến thành câu thử ([guide 2.3](02-guide.md#b2-3)): nguồn sự thật · mơ hồ, thiếu thông tin · ngoài phạm vi, thẩm quyền · đặc thù giáo dục.
4. **Mô tả hệ thống đang có phải có nguồn** (ảnh chụp tài khoản của mình đã che thông tin, trang chính thức). Không kiểm được thì ghi "chưa kiểm".

<a id="7-hang-muc"></a>
## Bài của nhóm là một câu chuyện — 7 hạng mục bắt buộc

**Pain → Impact → Giải pháp AI**, chống lưng bằng **Đánh giá** và **Mô phỏng chi phí**. Thiếu một mắt xích thì câu chuyện không đứng được.

| # | Hạng mục | Trả lời câu hỏi | Mức tối thiểu | Làm ở | Nằm ở file |
|---|---|---|---|---|---|
| 1 | **Bằng chứng pain** | Ai đau, đau thế nào, bao nhiêu người? | ≥1 nguồn đạt ngưỡng: **đào data** (x/N và %, cách đếm kiểm lại được) · **phỏng vấn** ≥3 người · **khảo sát** ≥20 người (ngoài nhóm, đúng người dùng) · ≥5 trích dẫn / ví dụ nguyên văn. Mạnh nhất: đào data rồi kiểm lại bằng phỏng vấn hoặc khảo sát | [1.2](02-guide.md#b1-2) | `evidence/` |
| 2 | **Impact có số** | Mỗi tháng mất bao nhiêu, vì sao chọn bài này? | Số người × số lần / tháng × tốn bao nhiêu mỗi lần, mỗi số có nguồn | [1.3](02-guide.md#b1-3) | `spec.md` |
| 3 | **Thiết kế giải pháp AI** | AI quyết định gì, dựa trên dữ liệu và công cụ nào, chặn rủi ro ở đâu, người duyệt ở đâu? | 1 sơ đồ: hình dạng (workflow / 1 agent / nhiều agent) + lý do · dữ liệu và công cụ AI dùng · chỗ chặn rủi ro · chỗ người duyệt | [2.2](02-guide.md#b2-2) | `spec.md` |
| 4 | **Bản chạy thử làm trọn lát cắt** | Người dùng đưa gì vào, AI quyết định gì, ra cái gì dùng được? | Gọi AI thật · quyết định dựa trên dữ liệu / công cụ của bài toán · chạy được bằng `run.py eval` và `run.py simulate` | [3.2](02-guide.md#b3-2) | `codebase/` |
| 5 | **Định nghĩa "tốt" + bộ câu thử** | Thế nào là đủ tốt với người dùng, và giải pháp đúng được bao nhiêu? | Data card · 20–30 câu thử · metric spec ≥3 metric · chuẩn "đạt" chốt ở CP2 · lượt 1 → lượt 2 | [2.4](02-guide.md#b2-4), [4.1](02-guide.md#b4-1) | `data/`, `eval/` |
| 6 | **Mô phỏng chi phí khi dùng thật** | Dùng thật cho cả khoá thì tốn bao nhiêu mỗi tháng, có đáng so với impact? | ≥50 phiên giả lập chạy qua bản chạy thử → chi phí / task thành công → 3 kịch bản ở quy mô thật | [4.2](02-guide.md#b4-2) | `cost/` |
| 7 | **Slide + demo + video dự phòng** | Kết luận go / iterate / stop dựa trên số nào? | `demo-slides.pdf` có trang "Đánh giá thế nào" và "Chi phí khi dùng thật" | [5.1](02-guide.md#b5-1) | thư mục gốc repo |
| + | *Bonus:* người dùng thử | Người dùng thật dùng được không, đổi gì sau khi thử? | 2–3 người ngoài nhóm dùng thử, có log | [4.3](02-guide.md#b4-3) | `validation/` |

**Thiếu hạng mục 1, 4, 5 (bộ câu thử + % đạt) hoặc slide PDF → không xét giải** (vẫn được chấm điểm lab). Cách chấm: [03-rubric.md](03-rubric.md).

## 5 câu tự kiểm bài toán — trước CP1 (17:00 Thứ Sáu 27/11) và trước khi chốt lát cắt ở CP2 (19:30)

| # | Tiêu chí | Đạt khi |
|---|---|---|
| 1 | Pain cụ thể | Ai, đang làm gì trong khoá, vướng ở đâu, hậu quả gì. "Mọi người thấy bất tiện" là chưa đạt |
| 2 | Có đường ra bằng chứng | Biết sẽ lấy bằng chứng từ nguồn nào (đào data · phỏng vấn ≥3 · khảo sát ≥20) và gặp được người dùng trong hai ngày. Ngưỡng: [guide 1.2](02-guide.md#b1-2) |
| 3 | Mô tả vấn đề không có chữ AI | Bỏ AI đi, việc đó vẫn tồn tại. Có ≥3 hướng để so trong bảng impact |
| 4 | Lát cắt đủ nhỏ | Đúng một câu theo mẫu trên, demo được trong 2 phút |
| 5 | Đo được và tính được tiền | Viết được "thế nào là tốt" thành câu thử có đáp án kiểm được, và biết người dùng dùng bao nhiêu lần / tháng để mô phỏng chi phí |

---

**Đọc tiếp:** chọn track ở [tracks/README.md](tracks/README.md) → đọc kỹ file track của nhóm → làm theo [02-guide.md bước 1.0](02-guide.md#b1-0).
