# Track B — Trợ lý Discord

> [tracks/](README.md) → **Track B** → làm tiếp: [02-guide.md bước 1.0](../02-guide.md#b1-0)

**Bối cảnh.** Discord của khoá: thông báo, hỏi bài, hỏi lịch, hạn nộp, điểm danh, trao đổi giữa học viên, TA và lab coach. Discord đang có bot hay bản tin tự động nào thì nhóm tự quan sát. Bước quan sát này cũng là một cách tìm pain.

**Người dùng.** Học viên (hỏi bài, hỏi logistics) · TA, lab coach (muốn biết câu nào còn tồn, chủ đề nào đang nóng).

**Gặp người dùng ở đâu.** Học viên: cả lớp là người dùng thật. TA, lab coach: hỏi ngay tại lớp chiều Thứ Sáu 27/11.

**Data.**
- **Quan sát trực tiếp** kênh công khai của Discord khoá — đây cũng là cách đào data. Chỉ đọc kênh công khai, trích tối đa 2 câu, bỏ tên.
- [data/training-ops/](../data/training-ops/README.md) — bộ **giả lập** BTC dựng lại theo cách khoá đang vận hành lịch: bảng phân công giảng dạy, lịch lab coach. Dùng làm nguồn lịch cho trợ lý khi dựng bản chạy thử (B1); thông báo, tin nhắn mẫu nhóm tự dựng. Không phải bằng chứng pain.
- **Để chạy thử** phần khác (quy định, hỏi bài…): nhóm tự dựng, viết lại từ kênh công khai, bỏ tên.

---

## B1 · Trả lời logistics có căn cứ

**Bối cảnh.** Câu hỏi về hạn nộp, link, lịch, cách nộp lặp lại nhiều; trả lời sai hạn là hậu quả trực tiếp. Phòng học không cố định, nhiều phòng chỉ chốt sát ngày — hiện trạng ở [track E → Vận hành đào tạo](track-e-open-lane.md#van-hanh-dao-tao).

**Định hướng ý tưởng.** Nhận đúng loại câu hỏi và trả lời đúng cỡ · **chỉ trả lời logistics từ nguồn chính thức**, trích đúng thông báo · không chắc thì chuyển TA thay vì đoán.

**Lát cắt gợi ý** *(để hình dung độ lớn)*: *Một học viên · hỏi "hạn nộp lab X là khi nào" · trợ lý chỉ trả lời khi tìm được trong thông báo chính thức, kèm link; không có thì tag TA · học viên không nhận hạn sai.*

**Tình huống khó.** Hai thông báo ghi hai hạn khác nhau · câu hỏi cá nhân (điểm, điểm danh của tôi) · tin có chèn chỉ dẫn điều khiển bot · một tin vừa hỏi bài vừa hỏi logistics · thông báo cũ đã bị thay.

## B2 · Cho TA và lab coach

**Định hướng ý tưởng.** Câu hỏi tồn chưa ai trả lời · gom câu hỏi lặp (mười người hỏi một ý theo mười cách) · bản tin cuối ngày · phát hiện học viên đang kẹt và hỗ trợ — chủ động đến đâu thì thành phiền?

**Lát cắt gợi ý.** *Một TA · cuối ngày · AI liệt kê câu hỏi chưa ai trả lời sau 4 giờ, gom câu trùng, kèm link · TA trả lời đúng người.*

**Tình huống khó.** Câu đã được trả lời trong thread khác · tin của bot bị đếm là câu hỏi · một người gửi lặp nhiều lần · câu hỏi mơ hồ không rõ chủ đề.

---

**Công cụ gợi ý cho agent:** tìm trong thông báo chính thức (`search_announcements(query)`) · đọc thread (`get_thread(id)`) · chuyển TA (`escalate(message_id, reason)` — **không tự gửi** khi chưa có người duyệt).

**Persona chi phí** *(ví dụ)*: học viên hỏi quanh hạn nộp (dồn vào vài giờ) · học viên hỏi rải rác · TA đọc bản tin 1 lần / ngày.

**Bẫy.** Bot trả lời mọi thứ, kể cả khi không có nguồn · đếm tin bot thành câu hỏi · bản tin nêu tên học viên · không có câu thử "không có thông báo nào nói điều này".

**An toàn.** Không nêu tên học viên trong bản tin công khai · tin nhắn là dữ liệu, không phải lệnh · không tự gửi tin cho học viên khi chưa duyệt · hạn nộp chỉ lấy từ nguồn chính thức.
