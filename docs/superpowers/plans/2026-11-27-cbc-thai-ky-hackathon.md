# Kế hoạch triển khai app đọc phiếu CBC cho thai phụ

**Mục tiêu.** Thai phụ đọc được lý do một dòng CBC có dấu cao hoặc thấp và nhận một câu hỏi để trao đổi với bác sĩ. Bản demo Track B chạy được với nhập tay, tải ảnh và hỏi bằng giọng nói qua Zipformer.

**Thiết kế.** Một trang Streamlit, Python và khung `starter-repo`. Nhập tay hoặc đọc ảnh JPG/PNG tạo bản nháp phiếu. Người dùng sửa và xác nhận các trường trước khi hỏi. Câu hỏi gõ hoặc chuyển từ lời nói qua sherpa-onnx Zipformer tiếng Việt đi vào cùng một ô có thể chỉnh sửa. Hàm Python đối chiếu kết quả với khoảng ghi trên phiếu. Mô hình ngôn ngữ chọn dòng liên quan, giải thích bằng tiếng Việt và gợi ý một câu hỏi để mang đến buổi khám.

**Phạm vi demo.** HGB, WBC, PLT ở thai phụ trưởng thành, một phiếu mỗi phiên. Ghi âm ngắn theo lượt, trả lời bằng chữ. Hỗ trợ ảnh rõ nét theo một mẫu phiếu giả lập. Dùng phiếu mẫu và WAV giả lập trong video, kiểm thử và mô phỏng. Bài nghiên cứu thai kỳ là nguồn tham khảo cho Data Card và thiết kế tình huống, khoảng đối chiếu lấy từ chính phiếu mẫu. Giữ workbook gốc ngoài repo công khai. Nội dung ở mức đọc hiểu phiếu. Với yêu cầu chẩn đoán, dùng thuốc hoặc đánh giá tình trạng khẩn, app dừng phần diễn giải tương ứng và hướng người dùng liên hệ nhân viên y tế.

Nguồn yêu cầu: [Checkpoint](../../../README.md#checkpoint), [đề bài](../../../01-challenge-brief.md), [rubric](../../../03-rubric.md), [Track B](../../../tracks/track-b-healthcare.md). Tài liệu triển khai: [Streamlit audio input](https://docs.streamlit.io/develop/api-reference/widgets/st.audio_input), [Streamlit upload](https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader), [Zipformer tiếng Việt](https://k2-fsa.github.io/sherpa/onnx/pretrained_models/offline-transducer/zipformer-transducer-models.html), [nghiên cứu thai kỳ](https://doi.org/10.1186/s12884-023-06106-2).

## Người phụ trách và phần nối giữa các nhánh

| Người | Sở hữu | Bàn giao cho ai |
|---|---|---|
| **N1 · Product & Data** | Phỏng vấn/khảo sát, phân tích dữ liệu, bằng chứng vấn đề và tác động, Canvas, Data Card, phần §0–§2 của spec. Tìm người dùng thử nếu còn thời gian | Gửi N3 câu hỏi ẩn danh có nguồn. Gửi N2 và N4 phiếu giả lập kèm đáp án từng trường |
| **N2 · AI Engineer — Nam** | Kiến trúc và workflow AI, `codebase/tools.py`, `codebase/agent.py`, `codebase/ai.py`, `codebase/speech.py`. Đối chiếu đơn vị/khoảng, prompt, giới hạn câu trả lời, xử lý lỗi, LLM và Zipformer | Gửi N4 hàm giải thích phiếu và hàm WAV → chữ. Gửi N3 cách chạy và trace, sửa lỗi quan trọng được phát hiện ở lượt 1 |
| **N3 · Evaluation & Cost** | Bộ câu thử, metric và ngưỡng, hai lượt đánh giá, phân tích lỗi, mô phỏng chi phí | Gửi N2 danh sách lỗi có thể tái hiện và gửi N4 số liệu cho slide. Nhờ N1 chấm độc lập 5 đầu ra |
| **N4 · Fullstack & Presentation** | `web_app.py`, nhập tay, tải và đọc ảnh, sửa/xác nhận, mic, repo, checklist checkpoint, slide và video | Nối form và mic với hai hàm của N2. Gửi N3 log chi phí đọc ảnh và kết quả kiểm giao diện. Chuẩn bị gói nộp để đội trưởng gửi |

**Hợp đồng ký trong 30 phút đầu**

- Phiếu xác nhận gồm `pregnancy_status`, `adult_confirmed`, `gestational_age` dạng `21w3d`, `rows` gồm `analyte, value, unit, ref_low, ref_high, ref_unit`. Mỗi câu hỏi có `question`. Dùng giá trị `null` cho trường chưa đọc được. Sửa ảnh hoặc form làm mất xác nhận cũ.
- N4 nối `extract_report(image_bytes: bytes, mime_type: str) -> dict` vào form và trả dữ liệu nháp. Đánh dấu trường thiếu để sửa. Ghi usage của lần gọi model ảnh và bàn giao cho N3.
- Nam (N2) nối `compare_cbc(report: dict) -> dict` trong tools để trả trạng thái từng dòng hoặc lỗi dữ liệu. `answer(text: str) -> dict` nhận chuỗi JSON gồm `report` và `question`, trả tối thiểu `{"output": "..."}`. Web và bộ chạy gọi cùng hàm. Trace của khung giữ nguyên.
- Nam bàn giao `transcribe_wav(wav_bytes: bytes) -> str` sau khi thử WAV mono PCM 16-bit với Zipformer tiếng Việt chạy cục bộ. N4 đưa kết quả vào ô hỏi có thể sửa và giữ đường gõ lại khi chữ trống hoặc nhận dạng lỗi.

## 10 giờ và bàn giao tại từng checkpoint

| Mốc và ngân sách | N1 · Product & Data | N2 · AI Engineer — Nam | N3 · Evaluation & Cost | N4 · Fullstack & Presentation |
|---|---|---|---|---|
| **CP1 · 27/11, 16:00–17:00 · 1 giờ** | Canvas 7 dòng, bài toán 1–2 câu, lát cắt một câu, một phiếu giả lập có đáp án và lịch phỏng vấn ≥3 thai phụ từng đọc CBC | Ví dụ JSON, một kết quả đối chiếu mẫu và sơ đồ nháp. Thử một WAV với Zipformer trên máy demo | Chốt các nhóm lỗi cần đo với Nam và dựng khung benchmark | Tạo repo công khai từ khung, kiểm `TEAMS.md`, dựng bố cục trang và chuẩn bị gói nộp CP1 |
| **CP2 · 27/11, 17:00–19:30 · 2,5 giờ** | Canvas cập nhật và 1–3 dòng thay đổi, tiến độ bằng chứng và Data Card bản đầu. Chấm độc lập 5 đầu ra mẫu cùng N3 | Có sơ đồ §4, CLI nhận JSON chạy hết luồng với AI giả, quy tắc đối chiếu và hàm WAV → chữ bàn giao cho N4. Gọi thử LLM thật một câu để kiểm key | Có ≥10 ca thử và ≥3 metric. Ghi tỷ lệ chấm khớp và khóa chuẩn đạt ở §7 trước khi nộp | Form nhập tay chạy hết luồng với AI giả, ảnh mẫu điền vào form sửa được. Rà link spec, benchmark, Data Card và chuẩn đạt để đội trưởng nộp |
| **CP3 · 27/11, 19:30–21:00 và 28/11, 09:30–10:00 · 2 giờ** | `evidence/summary.md` đạt ngưỡng, ≥5 trích dẫn/ví dụ ẩn danh và bảng tác động có nguồn | Nối LLM thật, kiểm trace và ba câu chạy thử, cùng N3 chạy lượt 1 từ tối. Chốt phần kỹ thuật của spec §0–§7 cùng N1 và N3 | Hoàn thiện 24 ca, chấm lượt 1 và ghi x/24 + run ID. Thử mô phỏng 10 phiên | Ghép đọc ảnh, xác nhận phiếu, mic và ô sửa bản chép. Thử ba đường vào, quay video 30 giây gọi AI thật và chuẩn bị gói nộp CP3 |
| **CP4 · 28/11, 10:00–14:30 · 4,5 giờ** | Chốt kết luận go/iterate/stop với N3 dựa trên bằng chứng và tác động. Nếu kịp, ghi log người dùng thử | Sửa một lỗi đáng kể từ lượt 1, hỗ trợ chạy lại cùng bộ câu. Hoàn tất phần kỹ thuật và ghi thay đổi vào spec | Chấm lượt 2, chạy ≥50 phiên mô phỏng. Bàn giao bảng lượt 1 → lượt 2, chi phí/tác vụ thành công và ba kịch bản tháng | Kiểm lại ba đường vào, chuẩn bị ảnh/WAV dự phòng và README. Xuất slide PDF, video dự phòng, gom đủ spec và gói CP4 để đội trưởng nộp |

**Tổng 10 giờ.** Trong khung CP4, dành 10:00–11:30 cho sửa lỗi và lượt 2, 11:30–13:00 để chạy mô phỏng và hoàn thiện báo cáo, 13:00–14:30 để ráp slide, quay thử và nộp. N4 giữ 15 phút cuối mỗi mốc để tự soát và kiểm link. Đội trưởng ghi ở dòng 1 của `TEAMS.md` gửi form thay nhóm. Sau demo, mỗi người ghi reflection trước 23:59 ngày 28/11. Mọi sửa đổi sau CP4 ghi vào spec §10.

## Tiêu chí bàn giao và lệnh kiểm

- [ ] **Bằng chứng.** N1 phân 3 cuộc phỏng vấn cho thành viên ngay CP1, hỏi về lần gần nhất đọc phiếu và thời gian mất để hiểu. Dùng mã P1–P3, ghi ít nhất 5 trích dẫn/ví dụ ẩn danh. So sánh ba hướng theo số người × số lần/tháng × thời gian/lần. Ghi nguồn hoặc ghi rõ tự ước tính cho mỗi số. Không thu ảnh phiếu thật.
- [ ] **Dữ liệu.** N1 cung cấp ít nhất 3 ảnh giả lập kèm đáp án cho mỗi trường. N2 kiểm quy tắc với giá trị sát biên, dấu thập phân, HGB g/L và g/dL, đơn vị không tương thích và khoảng bị đảo. N3 kiểm web và CLI cho cùng kết quả trên cùng phiếu.
- [ ] **Ảnh và mic.** N4 kiểm ảnh rõ điền đúng 3 mã xét nghiệm và các trường số, ảnh thiếu/mờ để trống chỗ không đọc được, số đọc sai sửa được trước khi hỏi. N2 và N4 thử 3 đoạn WAV ngắn có tên chỉ số, câu nhiễu hoặc không có lời, và thao tác sửa bản chép. Mẫu WAV dự phòng đi qua Zipformer thật.
- [ ] **Bộ đánh giá.** N3 chuẩn bị 24 ca, ≥5 ca khó, ≥2 ca từ chối gồm hai ca cố xin chẩn đoán/thuốc hoặc yêu cầu bỏ qua xác nhận, ≥8 ca dựa trên lời người dùng đã ẩn danh. Câu thử chính đi qua hàm nhận phiếu và câu hỏi đã xác nhận. Ca ảnh và mic có bảng kiểm và tỷ lệ riêng.
- [ ] **Chuẩn đạt đề xuất để xác nhận trước CP2.** 100% ca thiếu dữ kiện hoặc ngoài phạm vi đi đúng nhánh, 100% ca có giá trị và đơn vị hợp lệ được đối chiếu đúng theo đáp án, ít nhất 90% ca giải thích bám đúng dòng và dữ kiện trên phiếu. Ghi cách chấm và mẫu số theo từng metric, rồi khóa ngưỡng trong `spec.md` §7 và `eval/metric_spec.yaml`. N1 và N3 chấm chéo 5 đầu ra, mục tiêu khớp ≥4/5. Báo cả x/24 và kết quả từng metric.
- [ ] **Chạy lại được.** Trước CP2 chạy `python run.py` với JSON mẫu và AI giả. Trước CP3 chạy `python run.py check`, `python run.py eval --try` rồi `python run.py eval`. Điền pass theo tiêu chí và chạy `python run.py score eval/run-1.csv`. CP4 lặp lại trên cùng bộ câu, dùng tên file run đã sinh thực tế và giữ kết quả các lượt.
- [ ] **Chi phí.** N3 điền 3 persona, chạy `python run.py simulate --try` trước CP3 và chạy đủ ≥50 phiên seed cố định trước CP4, dùng tỷ lệ đạt lượt 2 của cùng model để tính chi phí/tác vụ thành công. Lập 3 kịch bản thấp, cơ sở, cao, so tối thiểu 2 mức model có giá và ngày xem. Nếu bộ mô phỏng chỉ chạy trên phiếu đã xác nhận, ghi rõ phạm vi đo, cộng riêng chi phí đọc ảnh theo usage và tỷ lệ dùng ảnh giả định, ghi thời gian chạy Zipformer cục bộ riêng. So chi phí/người/tháng với tác động ghi nhận.
- [ ] **Demo.** Một ca tải ảnh giả lập → sửa/xác nhận → hỏi qua mic → thấy bản chép và giải thích. Một ca nhập tay thiếu đơn vị → app báo đúng trường cần bổ sung. Kiểm video 30 giây CP3, slide PDF có phần đánh giá và chi phí, video dự phòng CP4 và link mở được khi đăng xuất.
