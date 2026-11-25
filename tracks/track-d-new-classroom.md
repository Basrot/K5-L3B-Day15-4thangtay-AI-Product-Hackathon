# Track D — Lớp học kiểu mới

> [tracks/](README.md) → **Track D** → làm tiếp: [02-guide.md bước 1.0](../02-guide.md#b1-0)

**Bối cảnh — một concept mẫu, không phải giới hạn.** Trang pre-class của khoá ([preclass-online.com](https://preclass-online.com)) đang có **lớp học AI**: học viên học cùng một trợ giảng AI và các bạn học AI với tính cách khác nhau; một bộ điều phối quyết định khi nào cho bạn học AI xen vào bài giảng. Có chế độ chỉ trợ giảng AI, có chế độ học cùng cả lớp AI. Đây chỉ là **một** dạng lớp học kiểu mới. Track D mở cho **mọi kiểu lớp học mới** mà AI làm khả thi: nhóm có thể lấy lớp học AI này làm điểm xuất phát, làm khác hẳn, hoặc dựng concept của riêng mình.

**Câu hỏi lớn của track.** Trải nghiệm học nào khiến học viên **chủ động hơn, hiểu sâu hơn, nhớ lâu hơn** — và AI làm được gì mà một giảng viên không làm nổi với hàng trăm người? Nghiên cứu học tập cho cùng một kết luận: người học học nhiều hơn khi **tương tác và tự kiến tạo** hơn là nghe và đọc (ICAP — Chi & Wylie, 2014); **thử và sai trước khi được giảng** (Productive Failure — Kapur) và **học bằng cách dạy lại** (Protégé effect — Chase và cộng sự, 2009) đều có hiệu quả đo được. Trước đây các cách này tốn người; agent làm chúng khả thi ở quy mô lớn.

**Người dùng.** Học viên đang học một bài cụ thể (cả lớp là người dùng thật) · giảng viên thiết kế, duyệt kịch bản tương tác.

**Gặp người dùng ở đâu.** Chính các bạn cùng khoá — ai cũng đã học trên trang pre-class.

**Data.**
- [data/preclass/](../data/preclass/README.md) — nhật ký hành vi thật (đã ẩn danh): học viên, trợ giảng AI, bạn học AI, bộ điều phối. Đọc từ điển cột và mục "Lưu ý khi đếm" trước.
- **Để chạy thử:** nhóm tự dựng nội dung bài từ bài pre-class của khoá (trích ngắn hoặc viết lại, có đánh mã đoạn).

**Riêng track D.** Vì đây là trải nghiệm học, chuẩn "đạt" phải có **≥1 chỉ số về học** (trả lời đúng sau khi học, giải thích lại được, thời gian tới lời giải) — không chỉ "AI trả lời đúng".

---

| Hướng | Định hướng ý tưởng | Lát cắt gợi ý (để hình dung độ lớn) | Tình huống khó |
|---|---|---|---|
| **D1 · Điều phối và cá nhân hoá lớp học AI** | Nhiều vai (trợ giảng, bạn học hay hỏi, bạn học suy nghĩ sâu…) phải **bám đúng nội dung bài**, giữ vai nhất quán, biết **khi nào im** để học viên tự nghĩ, và chỉnh theo từng người. Đây là đề duy nhất mà **nhiều vai là bản chất** | *Một học viên · đang xem một đoạn bài · bộ điều phối quyết định có cho một bạn học AI xen vào không, ai, kiểu gì · học viên trả lời được câu kiểm tra sau đoạn đó* | Hai vai nói chồng nhau · bạn học AI hiểu sai mà nói quá thuyết phục · học viên im lặng / trả lời một chữ · học viên hỏi ngoài bài |
| **D2 · Học từ lỗi** | Học viên làm bài **trước** khi được giảng; sai thì AI chẩn đoán đúng giả định sai và gợi ý một bước, kèm đoạn bài liên quan; đúng thì hỏi ngược để chắc là hiểu | *Một học viên · làm một bài trước khi xem video · sai, AI chỉ đúng chỗ hiểu sai + một gợi ý · học viên tự sửa và giải thích được* | Đoán đúng mà không hiểu · lỗi chưa từng gặp · cùng một lỗi lần thứ ba · lỗi nằm ở đề chứ không ở học viên |
| **D3 · Học bằng cách dạy** | Học viên **dạy lại** một khái niệm cho bạn học AI; bạn học AI hỏi ngược đúng chỗ giải thích còn hổng hoặc sai (đối chiếu với bài), chỉ "hiểu" khi giải thích đủ đúng | *Một học viên · dạy lại một khái niệm · bạn học AI hỏi ngược 2 câu đúng chỗ thiếu căn cứ · học viên bổ sung được ví dụ đúng* | Giải thích đúng nhưng khác cách nói của bài · sai mà tự tin · dán nguyên đoạn bài · AI "hiểu" quá dễ |
| **D4 · Game hoá** | Biến việc học trước buổi thành trò chơi có mục tiêu: AI quản trò chỉnh độ khó theo người, nhiệm vụ theo bài, đấu đội — nhưng **vẫn bám đúng kiến thức** | *Một học viên · làm chuỗi 5 nhiệm vụ của một bài · AI tăng / giảm độ khó theo kết quả · học viên hoàn thành và đúng câu kiểm tra cuối* | Câu đố sai kiến thức · lộ đáp án · học viên "cày điểm" mà không học · quá khó nên bỏ |

Nhóm có thể đề xuất lớp học kiểu mới khác — không cần dựa trên lớp học AI ở trên — nếu trả lời được bốn câu: **học viên phải làm gì chủ động** mà hiện nay không làm? **AI giữ đúng nội dung bằng cách nào** (bám nguồn nào, khi nào nói "không biết")? **Thích ứng theo cái gì** của từng người? **Đo "học được" bằng gì?**

---

**Công cụ gợi ý cho agent:** lấy đoạn bài theo mã (`get_passage(code)`) · đọc trạng thái người học (`learner_state(id)` — lỗi vừa mắc, lịch sử) · chấm câu trả lời theo đáp án (`check_answer(q, a)`) · bộ điều phối chọn vai nói tiếp (`next_speaker(state)`).

**Persona chi phí** *(ví dụ)*: học viên học 1 bài / ngày · học dồn cuối tuần · học viên tương tác nhiều (mỗi lượt gọi nhiều vai — token nhân lên theo số vai).

**Bẫy.** Làm chatbot nhiều tên mà vai không khác nhau · chỉ đo AI trả lời đúng, không đo học viên học được · nhiều vai làm chi phí nhân lên mà không tính · so hai chế độ học trên data quá ít.

**An toàn.** Bạn học AI "hiểu sai" phải được **sửa đúng trước khi kết thúc phiên** · nói rõ đây là AI, không giả làm người thật · không làm học viên nản khi sai · lỗi cá nhân không công khai cho lớp · giảng viên duyệt kịch bản.
