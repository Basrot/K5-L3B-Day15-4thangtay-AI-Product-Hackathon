# Reflection — Trần Trọng Đức Tài

> Làm ở guide bước 5.3. Thành viên **N4 · Fullstack & Presentation** (`2A202603732`) · Nhóm **4thangtay** · Lớp **L3B** · Track **F**.

1. **Vai trò + phần mình làm (trỏ tới file / commit):**
   Mình phụ trách khối **Fullstack & Presentation (N4)**: xây dựng giao diện web Next.js cho mẹ bầu và cổng bác sĩ (`frontend/src/app/page.tsx`, `frontend/src/app/portals.tsx`, `frontend/src/app/doctor/page.tsx`, `frontend/src/app/symptom-safety.tsx`), luồng tải ảnh/PDF tạo bản nháp bắt buộc kiểm tra và xác nhận lại trước khi hỏi AI, thu âm microphone trình duyệt đổi sang `WAV PCM 16 kHz` (`frontend/src/lib/audio.ts`), phát giọng đọc `VieNeu TTS`, so sánh lịch sử nhiều phiếu theo ngày lấy mẫu, bản tóm tắt in PDF cho buổi khám và phối hợp hoàn thiện bộ slide thuyết trình (`slides/demo-slides.html`, `demo-slides.pdf`) cùng kịch bản demo.

2. **AI hỗ trợ mình thế nào (việc gì, công cụ gì, chỗ nào phải sửa lại output AI):**
   Mình sử dụng trợ lý lập trình AI để dựng nhanh bố cục component React/Tailwind theo tông màu chăm sóc thai kỳ, viết hàm chuyển đổi `AudioBuffer` sang `WAV 16 kHz` trên trình duyệt và đồng bộ client gọi API (`frontend/src/lib/api.ts`, `frontend/src/lib/types.ts`). Khi tích hợp thực tế, mình phải chỉnh sửa lại nhiều chi tiết UX mà code AI sinh ban đầu chưa xử lý chặt: gắn `AbortController` và kiểm tra `revision` để hủy ngay kết quả cũ mỗi khi người dùng sửa bất kỳ ô số liệu nào trên phiếu (`invalidateReport`), giữ nguyên các ô đơn vị trống từ OCR thay vì tự điền ngầm đơn vị mặc định, và hiển thị rõ thẻ dữ kiện đã xác nhận tách biệt với lời giải thích của trợ lý.

3. **Một câu thử trượt của nhóm và mình học được gì từ nó:**
   Qua câu thử trượt `B21` (phiếu có kết quả `RBC` nhưng để trống `ref_low/ref_high` và không khai báo rõ `reference_mode: lab`, dẫn tới hệ thống tự suy sang chế độ khoảng nghiên cứu `study`) và các ca thiếu đơn vị như `B20`, mình nhận ra giao diện đóng vai trò chốt chặn đầu tiên cho chất lượng đầu vào của AI. Nếu form nhập liệu để chế độ tham chiếu hoặc đơn vị mặc định không minh bạch, thai phụ rất dễ bấm xác nhận nhầm giữa khoảng in trên phiếu và khoảng nghiên cứu theo tuần thai; vì vậy thiết kế UI phải bắt buộc người dùng chọn rõ chế độ đối chiếu và kiểm nhận lại bản nháp trước khi mở khóa phần hỏi đáp.
