# Track E — Làn mở (trong phạm vi AI20K)

> [tracks/](README.md) → **Track E** → làm tiếp: [02-guide.md bước 1.0](../02-guide.md#b1-0)

**Định hướng ý tưởng.** Một pain thật trong việc học và dạy ở chính khoá AI20K mà track A–D chưa chạm tới — và một sản phẩm AI cho nó.

**Phạm vi — bắt buộc.** "Mở" là mở về **bài toán**, không mở về **bối cảnh**. Sản phẩm phải phục vụ người trong khoá: học viên, giảng viên, TA, lab coach, ban đào tạo, đội sản xuất nội dung. **Không hợp lệ:** sản phẩm cho thị trường ngoài, app tiêu dùng chung chung, "AI cho giáo dục" không gắn với một người dùng cụ thể của khoá. Không chỉ ra được người dùng trong khoá mà nhóm gặp được trong hai ngày → không thuộc track E.

**Điều kiện.** Cùng luật, cùng guide, cùng rubric như mọi track. Bằng chứng pain và bảng impact được soi kỹ hơn vì không có sản phẩm sẵn để dựa vào. **Cho lab coach xem thẻ đề của nhóm** (khung bên dưới) tại lớp, trước khi nộp CP1 lúc 17:00 Thứ Sáu 27/11.

---

<a id="van-hanh-dao-tao"></a>
## Hướng nổi bật · Vận hành đào tạo — lịch, phòng, phân công

**Hiện trạng.**
- **Khoá đang thiếu cơ sở vật chất, phòng học không cố định.**
  - Lớp L3 hơn 700 học viên, chia L3A và L3B. Mỗi buổi giảng (LEC) phải ghép hai phòng song song, thêm phòng phụ. Mỗi buổi lab rải 3–6 phòng ở nhiều khu.
  - Hôm nay lớp học khu này, hôm khác học khu khác.
- **Nhiều phòng chỉ được xác nhận sát ngày học**, có khi ngay trong ngày. Phòng đã xác nhận vẫn có thể đổi.
- **Phân công nằm ở nhiều bảng tính:**
  - Ban đào tạo mở form cho giảng viên đăng ký buổi, gom lại và rà trùng, rồi ghi giảng viên theo phòng vào một bảng lịch chung. Mỗi ô trong bảng là chữ tự do.
  - Đội lab coach giữ bảng riêng: lịch lab theo đợt, đổi ca qua form và nhóm Zalo, workload đếm ca.
- **Học viên** nhận lịch qua email, tra lớp và nhóm trong một link danh sách. Thông báo đi qua nhiều kênh: email, Discord, LMS.

**Định hướng ý tưởng.** Sắp xếp lịch và đưa lịch tới đúng người (phòng, giờ, giảng viên, lab coach), khi phòng chỉ chốt sát ngày và thông tin nằm ở nhiều nơi.

**Người dùng:**
- Ban đào tạo: xếp lịch, xin phòng.
- Key coach / Day Lead: chia coach theo phòng, gửi tài liệu trước buổi.
- Lab coach và giảng viên.
- Học viên: người nhận lịch. Cả lớp là người dùng thật.

**Gặp người dùng ở đâu.**
- Học viên: ngay trong lớp.
- Lab coach, key coach: tại lớp chiều Thứ Sáu 27/11.
- Ban đào tạo: hẹn qua lab coach.

Gợi ý: nhóm tự tìm và hỏi lab coach, key coach, ban đào tạo, ngay trong lớp hoặc hẹn riêng.

**Data.** [data/training-ops/](../data/training-ops/README.md) — bộ **giả lập** dựng lại bảng phân công giảng dạy (kèm lịch sử chỉnh sửa) và bảng lab coach theo đúng cấu trúc thật. Người được ghi bằng nhãn, ngày là ngày giả. Bộ này để hình dung và chạy thử, **không phải bằng chứng pain**. Bằng chứng phải lấy từ người dùng thật.

**Lát cắt gợi ý** *(để hình dung độ lớn, nhóm tự viết câu của mình)*:
- *Một key coach · tối trước buổi lab · AI đối chiếu phòng vừa xác nhận với lịch lab và danh sách nhóm, soạn thông báo phòng cho từng nhóm · key coach duyệt rồi gửi.*
- *Một người ở ban đào tạo · một phòng bị rút sát ngày · AI đề xuất 2–3 phương án phòng hoặc giờ thay thế, code kiểm trùng · người phụ trách chọn một.*

**Tình huống khó.**
- Phòng chưa xác nhận.
- Hai bảng ghi hai phòng khác nhau.
- Phòng đổi sau khi đã báo học viên.
- Một lớp tách nhiều phòng ở nhiều khu.
- Buổi chuyển sang online.
- Tên người gõ lệch so với danh sách chuẩn.

**Công cụ gợi ý cho agent:**
- Tra lịch theo ngày và lớp: `get_schedule(date, class)`.
- Kiểm trùng phòng, trùng người: `check_conflicts(plan)` — chạy bằng code, không phải AI.
- Soạn thông báo: `draft_notice(class, changes)` — **không tự gửi**.

**Persona chi phí** *(ví dụ)*:
- Ban đào tạo xếp lại lịch vài lần mỗi tuần.
- Key coach soạn thông báo mỗi tối trước buổi lab.
- Học viên hỏi dồn trước giờ học.

**Bẫy.**
- Để AI tự chốt phòng: phòng do trường cấp, AI chỉ đề xuất.
- Trả lời theo bảng cũ.
- Coi data giả lập là bằng chứng.

**An toàn.**
- Không gửi thông báo khi chưa có người duyệt.
- Không nêu tên học viên, coach trong thông báo công khai.

---

## Hướng gợi ý khác

**Luyện kỹ năng với nhân vật AI**
- **Khách hàng ảo để tập phỏng vấn.** Học viên tập phỏng vấn người dùng với một persona AI trước khi gặp người thật: persona trả lời nhất quán, không tự khai pain khi bị hỏi kiểu gợi ý, AI chỉ ra câu hỏi nào là câu dẫn dắt. *(Trò chuyện với persona ảo không tính là bằng chứng pain.)*
- **Giám khảo ảo / tập demo.** Agent đọc repo nhóm cùng rubric rồi hỏi vặn như giám khảo: thiếu bằng chứng ở đâu, số nào không có nguồn, chuẩn "đạt" có bị sửa không.

**Ví dụ khác trong khoá** *(để hình dung, không phải danh sách bắt buộc)*
- **Hỗ trợ làm lab** — gợi ý từng bước khi học viên kẹt, không đưa lời giải hoàn chỉnh.
- **Chấm và nhận xét theo tiêu chí** — phản hồi từng tiêu chí, giảng viên duyệt; AI không tự cho điểm cuối.
- **Cảnh báo sớm học viên tụt lại** — **chỉ dữ liệu giả lập**, AI chỉ gợi ý cho lab coach, đo cảnh báo nhầm.
- **Ghép nhóm / ghép mentor** — theo kỹ năng và giờ rảnh, người phụ trách duyệt.

Data cho các hướng khác nhóm tự thu và tự dựng ([01-challenge-brief → Data](../01-challenge-brief.md#data)).

---

## Thẻ đề của nhóm — viết theo khung này

Chép vào `canvas.md` (dưới bảng 7 dòng). Mỗi mục 1–3 dòng.

```markdown
# Track E · [tên đề ngắn]

**Pain.** Ai — đang làm gì trong khoá — vướng đâu — hậu quả gì. (Không có chữ AI.)
**Người dùng.** Vai chính · người hưởng lợi phụ · gặp họ ở đâu trong hai ngày.
**Data.** Đào từ đâu / tự thu gì / không dùng gì.
**Lát cắt.** Một câu: 1 người dùng · 1 việc · 1 quyết định AI · 1 kết quả.
**Công cụ của agent.** Tên · input · output · có tác động ra ngoài không.
**Bộ câu thử.** Câu thử trông thế nào, chấm đạt thế nào, câu nào phải từ chối.
**Persona chi phí.** Ít / vừa / nhiều dùng bao nhiêu lần.
**Bẫy.** 2–3 cách đề này dễ hỏng.
**An toàn.** AI không được làm gì; dữ liệu nào nhạy cảm.
```

**Lỗi hay gặp.** Đề nghe hay nhưng không ai trong khoá thật sự gặp → không có bằng chứng · chọn làn mở vì "đề có sẵn khó quá" → thường khó hơn, vì phải tự thu mọi dữ liệu · lát cắt quá to (cả một nền tảng) → không kịp trong ~10 giờ.

**An toàn.** Chỉ dữ liệu đã ẩn danh hoặc giả lập · không cố nhận diện ai · sản phẩm chạm tới điểm số, điểm danh, xếp hạng học viên phải có người duyệt — AI chỉ đề xuất.
