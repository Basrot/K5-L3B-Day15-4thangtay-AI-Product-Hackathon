# Track C — Sản xuất bài giảng online (video / tương tác)

> [tracks/](README.md) → **Track C** → làm tiếp: [02-guide.md bước 1.0](../02-guide.md#b1-0)

**Bối cảnh.** Track này nói về **sản xuất bài giảng bằng AI**. Model giờ sinh kịch bản, slide, video và bài tương tác rất tốt — sinh ra các định dạng học mới. Chỗ nghẽn đã chuyển sang khâu **kiểm và duyệt**: nội dung AI sinh có đúng kiến thức không, mỗi khẳng định lấy từ đâu, đoạn nào cần sửa, ai duyệt. Track này làm **agent hỗ trợ trong cả quy trình tạo bài giảng**: tìm và trích nguồn, rà soát, review, duyệt, sửa theo góp ý.

**Người dùng.** Giảng viên (tạo + duyệt) · đội sản xuất nội dung (viết kịch bản, dựng, biên tập) · với C3, C5: người học.

**Gặp người dùng ở đâu.** Giảng viên, lab coach, đội sản xuất bài giảng online: ít người, **hẹn từ sáng Thứ Sáu 27/11**. Nhóm tự tìm người để hỏi, hoặc nói chuyện trực tiếp với đội sản xuất bài giảng online của khoá. Người học (C3, C5): cả lớp là người xem bài giảng thật.

Nhóm cũng có thể **tự đề xuất ý tưởng riêng** trong mảng sản xuất bài giảng bằng AI. Các hướng C1–C5 dưới đây chỉ là gợi ý.

**Data.** Nhóm tự dựng từ bài giảng của khoá: đoạn transcript, kịch bản có mã câu, hồ sơ nguồn, dàn ý, slide. Không commit nguyên tài liệu khoá; chỉ trích đoạn ngắn hoặc viết lại.

---

| Hướng | Định hướng ý tưởng | Lát cắt gợi ý (để hình dung độ lớn) | Tình huống khó |
|---|---|---|---|
| **C1 · Rà soát kiến thức** | Kịch bản / video AI sinh → agent chỉ ra khẳng định sai hoặc thiếu nguồn, gắn đúng câu / mốc thời gian, đề xuất sửa tối thiểu → giảng viên chấp nhận / từ chối từng chỗ | *Một giảng viên · duyệt kịch bản 40 câu · AI đánh dấu câu thiếu nguồn hoặc sai kèm lý do · giảng viên duyệt từng chỗ* | Đoạn sạch (đo báo nhầm) · lỗi tinh vi chỉ chuyên gia thấy · nguồn mâu thuẫn nhau |
| **C2 · Nghiên cứu → kịch bản có nguồn** | Từ chủ đề + mục tiêu bài → agent tìm, chấm độ tin cậy nguồn, viết kịch bản mà **mọi câu khẳng định trỏ về một đoạn nguồn**; loại một nguồn thì chỉ viết lại câu phụ thuộc | *Một người viết · cần 5 câu mở đầu cho chủ đề X · AI tìm 3 nguồn, viết 5 câu mỗi câu gắn nguồn · người viết loại một nguồn → chỉ câu liên quan đổi* | Nguồn lỗi thời · số liệu không nguồn · nguồn uy tín thấp nhưng nghe thuyết phục |
| **C3 · Transcript → bài tương tác** | Biến một đoạn bài giảng thành bài tương tác: câu hỏi chen giữa video, câu ôn tập — mỗi câu trỏ về đúng đoạn nguồn, giảng viên duyệt | *Một giảng viên · có transcript 10 phút · AI đề xuất 3 câu hỏi chen kèm mốc thời gian và đoạn nguồn · giảng viên giữ / bỏ từng câu* | Câu hỏi đúng chữ nhưng sai ý · đáp án nằm ngoài đoạn · câu hỏi lộ đáp án |
| **C4 · Kế hoạch hình cho video** | Từ lời đọc đã chốt → mỗi câu: người xem cần thấy ý gì, hình gì, chữ gì trên màn hình, hiện lúc đọc tới từ nào | *Một người viết · lời đọc 10 câu · AI đề xuất hình + chữ cho từng câu · góp ý một câu thì chỉ câu đó đổi* | Câu trừu tượng khó vẽ · chữ trên màn hình quá dài · hình mâu thuẫn lời |
| **C5 · Góp ý người học → bản sửa** | Gom góp ý từ nhiều kênh về một video → định vị đúng đoạn, tách lỗi nội dung / kỹ thuật → đề xuất phạm vi sửa tối thiểu | *Một người dựng · 30 góp ý về một video · AI gom thành 5 vấn đề theo đoạn · người dựng chấp nhận / từ chối từng vấn đề* | Góp ý mơ hồ · góp ý trái ngược · mười người nói một ý |

---

**Công cụ gợi ý cho agent:** tìm trong tài liệu / web (`search_sources(query)`) · lấy đoạn theo mã (`get_segment(code)`) · đối chiếu khẳng định với nguồn (`check_claim(claim, source)`) · xuất bản nháp cho người duyệt (`submit_for_review(draft)` — **không tự xuất bản**).

**Persona chi phí** *(ví dụ)*: giảng viên soạn 1 bài / tuần (nhiều lượt, token lớn) · soát lại bài cũ (ít lượt, token rất lớn) · nếu sinh hình / video: thêm chi phí API hình / video, ghi nguồn giá.

**Bẫy.** Demo đẹp nhưng không đo được đúng / sai kiến thức · bỏ bước người duyệt · làm video tốn nhiều giờ — trong ~10 giờ nên dừng ở kịch bản, slide, sơ đồ · chỉ đo phát hiện lỗi mà không đo **báo nhầm** · không báo riêng **tỉ lệ bỏ sót lỗi** (nguy hiểm nhất).

**An toàn.** Không có gì đến tay học viên khi giảng viên chưa duyệt · ghi rõ phần do AI tạo · không giả làm giảng viên thật · không commit nguyên slide, transcript của khoá.
