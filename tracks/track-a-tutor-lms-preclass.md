# Track A — AI Tutor cho LMS và trang pre-class

> [tracks/](README.md) → **Track A** → làm tiếp: [02-guide.md bước 1.0](../02-guide.md#b1-0)

**Bối cảnh.** LMS và trang pre-class của khoá ([preclass-online.com](https://preclass-online.com)). Trước mỗi buổi, học viên xem video, làm câu hỏi giữa video và mini lab, hỏi trợ giảng AI ngay dưới video. Cuối ngày có phần ôn tập.

**Người dùng.** Học viên đang học trước buổi (chính) · giảng viên, lab coach muốn biết lớp đang kẹt ở đâu (phụ).

**Gặp người dùng ở đâu.** Học viên: chính các bạn cùng lớp, nhóm khác — phỏng vấn hoặc khảo sát được ngay trong giờ nghỉ. Giảng viên, lab coach: hẹn từ sáng Thứ Sáu 27/11.

**Data.**
- [data/preclass/](../data/preclass/README.md) — nhật ký hành vi thật (đã ẩn danh) của khoá trên trang pre-class. Đọc từ điển cột trước khi đếm.
- **Để chạy thử:** nhóm tự dựng 1–2 bài có đánh mã đoạn từ bài pre-class của khoá (trích ngắn hoặc viết lại, không commit nguyên bài) làm nguồn cho tutor.

---

## A1 · Tối ưu trợ giảng AI đang chạy

**Bối cảnh.** Trợ giảng AI đã chạy thật với nhiều lượt hỏi. Một trợ giảng tốt phải trả lời có căn cứ trong bài, đúng cỡ, hỏi lại khi câu hỏi mơ hồ, biết nói "không có trong bài".

**Định hướng ý tưởng.** Tìm **một** điểm trợ giảng đang làm chưa tốt — có bằng chứng — rồi cải thiện đến nơi đến chốn, đo được trước / sau trên bộ câu thử.

**Lát cắt gợi ý** *(để hình dung độ lớn, nhóm tự viết câu của mình)*: *Một học viên · hỏi một câu dưới video · trợ giảng tìm đoạn liên quan và quyết định trả lời kèm mã đoạn hay nói "không có trong bài" · học viên tự kiểm được bằng cách mở đúng đoạn.*

**Tình huống khó.** Câu hỏi ngoài bài · đoạn hỏi quá ngắn, vô nghĩa · học viên xin làm hộ bài · học viên dán chỉ dẫn "bỏ qua hướng dẫn trước đó" · câu hỏi đúng nhưng tài liệu thiếu.

## A2 · Tính năng AI mới trên LMS / trang pre-class

**Định hướng ý tưởng.** Một tính năng mới cho học viên hoặc giảng viên, xuất phát từ pain có bằng chứng. Ví dụ để hình dung (không phải danh sách bắt buộc): báo cáo một trang "lớp đang kẹt gì" cho giảng viên trước buổi · câu hỏi kiểm tra hiểu cuối bài, giải thích khi sai · trải nghiệm học bù cho người nghỉ buổi.

**Lát cắt gợi ý.** *Một giảng viên · trước buổi học · AI gom tín hiệu của lớp thành 3–5 chỗ khó nhất kèm ví dụ · giảng viên chọn chỗ để giảng lại.*

**Tình huống khó.** Data thưa (lớp hỏi ít) · một người tạo ra phần lớn tín hiệu · hai bài cùng nói một khái niệm · tín hiệu ngược nhau.

---

**Công cụ gợi ý cho agent** *(nhóm chọn theo thiết kế ở [bước 2.2](../02-guide.md#b2-2))*: tra đoạn bài theo câu hỏi (`search_lesson(query) → [mã đoạn, nội dung]`) · lấy đoạn theo mã (`get_passage(code)`) · đọc tín hiệu lớp đã tổng hợp (`class_signals(lesson_id)`).

**Persona chi phí** *(ví dụ — số thật lấy từ bằng chứng của nhóm)*: học viên hỏi ít · vừa · ôn dồn trước kiểm tra. Giảng viên đọc báo cáo: 1 lượt / buổi, token vào lớn.

**Bẫy.** Làm chatbot chung chung không gắn với bài · % trên một phần data bị hiểu thành % toàn khoá · đo "trả lời hay" thay vì "trích đúng nguồn" · dán nguyên tài liệu khoá vào repo công khai.

**An toàn.** Không cố đoán ai là ai từ data · không xếp hạng học viên · trợ giảng không "đoán chắc" khi không có căn cứ · giảng viên quyết định nội dung dạy.
