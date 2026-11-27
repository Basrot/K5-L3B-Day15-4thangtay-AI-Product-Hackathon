# Kế hoạch triển khai app đọc phiếu CBC cho thai phụ

**Mục tiêu.** Thai phụ đọc được lý do một dòng CBC có dấu cao hoặc thấp và nhận một câu hỏi để trao đổi với bác sĩ. Bản demo Track B chạy được với nhập tay, tải ảnh và hỏi bằng giọng nói qua Zipformer.

**Thiết kế.** Một trang Streamlit, Python và khung `starter-repo`. Nhập tay hoặc đọc ảnh JPG/PNG tạo bản nháp phiếu. Người dùng sửa và xác nhận các trường trước khi hỏi. Câu hỏi gõ hoặc chuyển từ lời nói qua sherpa-onnx Zipformer tiếng Việt đi vào cùng một ô có thể chỉnh sửa. Hàm Python đối chiếu kết quả với khoảng ghi trên phiếu. Mô hình ngôn ngữ chọn dòng liên quan, giải thích bằng tiếng Việt và gợi ý một câu hỏi để mang đến buổi khám.

**Phạm vi demo.** HGB, WBC, PLT ở thai phụ trưởng thành, một phiếu mỗi phiên. Ghi âm ngắn theo lượt, trả lời bằng chữ. Hỗ trợ ảnh rõ nét theo một mẫu phiếu giả lập. Dùng phiếu mẫu và WAV giả lập trong video, kiểm thử và mô phỏng. Bài nghiên cứu thai kỳ là nguồn tham khảo cho Data Card và thiết kế tình huống, khoảng đối chiếu lấy từ chính phiếu mẫu. Giữ workbook gốc ngoài repo công khai. Nội dung ở mức đọc hiểu phiếu. Với yêu cầu chẩn đoán, dùng thuốc hoặc đánh giá tình trạng khẩn, app dừng phần diễn giải tương ứng và hướng người dùng liên hệ nhân viên y tế.

Nguồn yêu cầu: [Checkpoint](../../../README.md#checkpoint), [đề bài](../../../01-challenge-brief.md), [rubric](../../../03-rubric.md), [Track B](../../../tracks/track-b-healthcare.md). Tài liệu triển khai: [Streamlit audio input](https://docs.streamlit.io/develop/api-reference/widgets/st.audio_input), [Streamlit upload](https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader), [Zipformer tiếng Việt](https://k2-fsa.github.io/sherpa/onnx/pretrained_models/offline-transducer/zipformer-transducer-models.html), [nghiên cứu thai kỳ](https://doi.org/10.1186/s12884-023-06106-2).

## Người phụ trách và phần nối giữa các nhánh

| Người | Sở hữu | Bàn giao cho ai |
|---|---|---|
| **N1 · Đội trưởng và sản phẩm** | Repo công khai, `TEAMS.md`, Canvas, bằng chứng, impact, spec, slide và nộp bài | Gửi N4 câu hỏi đã ẩn danh và nguồn, gửi N2/N3 bối cảnh và ca cần hỗ trợ |
| **N2 · Web và nhập phiếu** | `web_app.py`, form nhập tay, mẫu phiếu, tải và đọc ảnh, sửa và xác nhận. Ghi lệnh khởi chạy trong README | Gửi N3 phiếu đã xác nhận theo cấu trúc chung, gửi N4 ảnh giả lập và đáp án từng trường |
| **N3 · Quy tắc và AI trả lời** | `codebase/tools.py`, `codebase/agent.py`, `codebase/ai.py`. Đơn vị, khoảng tham chiếu, xử lý thiếu dữ kiện, gọi model thật và trace | Gửi N2 hàm dùng chung với CLI, gửi N4 cách chạy và log model/token. Hỗ trợ nối mic nếu N4 phải chạy benchmark |
| **N4 · Zipformer và đánh giá** | `codebase/speech.py`, mẫu WAV, bộ câu thử, tiêu chí đạt, hai lượt đánh giá và mô phỏng chi phí | Gửi N2 hàm chuyển WAV thành chữ trước khi viết giao diện mic. Nhờ N1 chấm độc lập 5 đầu ra và N2 đo riêng lượt đọc ảnh |

**Hợp đồng ký trong 30 phút đầu**

- Phiếu xác nhận gồm `pregnancy_status`, `adult_confirmed`, `gestational_age` dạng `21w3d`, `rows` gồm `analyte, value, unit, ref_low, ref_high, ref_unit`. Mỗi câu hỏi có `question`. Dùng giá trị `null` cho trường chưa đọc được. Sửa ảnh hoặc form làm mất xác nhận cũ.
- N2 nối `extract_report(image_bytes: bytes, mime_type: str) -> dict` vào form và trả dữ liệu nháp. Trường thiếu được đánh dấu để sửa. N2 bàn với N3 cách ghi usage của lần gọi model ảnh.
- N3 nối `compare_cbc(report: dict) -> dict` trong tools để trả trạng thái từng dòng hoặc lỗi dữ liệu. `answer(text: str) -> dict` nhận chuỗi JSON gồm `report` và `question`, trả tối thiểu `{"output": "..."}`. Web và bộ chạy dùng cùng entry point. Trace của khung giữ nguyên.
- N4 bàn giao `transcribe_wav(wav_bytes: bytes) -> str`. N2 đưa kết quả vào ô hỏi có thể sửa. N4 thử WAV mono PCM 16-bit với model tiếng Việt chạy cục bộ. Câu chữ trống hoặc lỗi nhận dạng có đường gõ lại.

## 10 giờ và bàn giao tại từng checkpoint

| Mốc và ngân sách | N1 · Sản phẩm | N2 · Web và ảnh | N3 · Quy tắc và AI | N4 · Giọng nói và đo lường |
|---|---|---|---|---|
| **CP1 · 27/11, 16:00–17:00 · 1 giờ** | Tạo repo công khai từ khung, điền TEAMS và Canvas 7 dòng. Chốt bài toán 1–2 câu, lát cắt 1 câu, hẹn ít nhất 3 thai phụ từng đọc phiếu CBC | Bàn giao bố cục trang và một phiếu JPG/PNG giả lập có đáp án | Bàn giao ví dụ JSON, một kết quả đối chiếu mẫu và sơ đồ luồng nháp | Bàn giao kết quả kiểm Zipformer trên máy demo với một WAV. Ghi 3 nhóm lỗi cần thử |
| **CP2 · 27/11, 17:00–19:30 · 2,5 giờ** | Tổng hợp phỏng vấn ban đầu, cập nhật Canvas và ghi 1–3 dòng thay đổi. Có link spec, sơ đồ §4, Data Card và chuẩn đạt ở §7 | Form nhập tay đi hết luồng với AI giả. Tải được ảnh mẫu và hiển thị form sửa trường. Thử model ảnh trên một fixture | Kiểm đơn vị, trường thiếu và khoảng nhập đảo. CLI nhận JSON và đi hết luồng với AI giả. Thử model thật một câu riêng để kiểm key | Hàm `transcribe_wav` chạy được và chuyển cho N2. Nộp ≥10 câu thử và ≥3 metric. N1 và N4 chấm độc lập 5 đầu ra mẫu, ghi tỷ lệ khớp |
| **CP3 · 27/11, 19:30–21:00 và 28/11, 09:30–10:00 · 2 giờ** | Bàn giao `evidence/summary.md` đạt ngưỡng, ≥5 trích dẫn hoặc ví dụ ẩn danh, spec §0–§7. Chốt impact có nguồn và quay video 30 giây có gọi AI thật | Tối ghép trích xuất ảnh thật, sửa/xác nhận phiếu và mic. Sáng thử lại một đường nhập tay, một đường ảnh và mic trên máy demo | Tối nối AI thật, kiểm trace và chạy thử 3 câu. Phối hợp chạy lượt 1 trước khi nghỉ để sáng còn thời gian chấm và xử lý lỗi kỹ thuật | Mở rộng lên 24 câu, chạy lượt 1 với N3, chấm và ghi x/24, run ID. Chạy thử mô phỏng 10 phiên. Ghi riêng kết quả mic/WAV và ảnh |
| **CP4 · 28/11, 10:00–14:30 · 4,5 giờ** | Hoàn tất spec §8–§10, kết luận go/iterate/stop dựa trên số, slide PDF và link video dự phòng. Nộp phòng demo, link repo và tình trạng các hạng mục | Soát ảnh thiếu hoặc mờ, nút sửa và luồng mic. Chuẩn bị ảnh/WAV dự phòng và README chạy trên máy demo | Sửa một lỗi có tác động từ lượt 1, hỗ trợ chạy lại đúng bộ câu, kiểm run ID và model. Cùng N2 quay demo dự phòng | Chạy và chấm lượt 2, đủ ≥50 phiên mô phỏng, báo chi phí/tác vụ thành công và 3 kịch bản tháng. Bàn giao bảng lượt 1 → lượt 2 và báo cáo chi phí |

**Tổng 10 giờ.** Trong khung CP4, dành 10:00–11:30 cho sửa lỗi và lượt 2, 11:30–13:00 để chạy mô phỏng và hoàn thiện báo cáo, 13:00–14:30 để ráp slide, quay thử và nộp. N1 giữ 15 phút cuối mỗi mốc cho tự soát, kiểm link và điền form. Sau demo, mỗi người ghi reflection trước 23:59 ngày 28/11. Mọi sửa đổi sau CP4 ghi vào spec §10.

## Tiêu chí bàn giao và lệnh kiểm

- [ ] **Bằng chứng.** N1 phân 3 cuộc phỏng vấn cho thành viên ngay CP1, hỏi về lần gần nhất đọc phiếu và thời gian mất để hiểu. Dùng mã P1–P3, ghi ít nhất 5 trích dẫn/ví dụ ẩn danh. So sánh ba hướng theo số người × số lần/tháng × thời gian/lần. Ghi nguồn hoặc ghi rõ tự ước tính cho mỗi số. Không thu ảnh phiếu thật.
- [ ] **Dữ liệu.** N2 cung cấp ít nhất 3 ảnh giả lập kèm đáp án cho mỗi trường. N3 thử giá trị sát biên, phân cách thập phân, HGB g/L và g/dL, đơn vị không tương thích và khoảng bị đảo. Kiểm Web và CLI cho cùng kết quả trên cùng phiếu.
- [ ] **Ảnh và mic.** N2 kiểm ảnh rõ điền đúng 3 mã xét nghiệm và các trường số, ảnh thiếu/mờ để trống chỗ không đọc được, ảnh có số đọc sai có thể được người dùng sửa trước khi hỏi. N4 kiểm 3 đoạn WAV ngắn có tên chỉ số, câu nhiễu hoặc không có lời và thao tác sửa transcript. Mẫu WAV dự phòng vẫn phải đi qua Zipformer thật.
- [ ] **Bộ đánh giá.** N4 chuẩn bị 24 ca, ≥5 ca khó, ≥2 ca từ chối gồm hai ca cố xin chẩn đoán/thuốc hoặc yêu cầu bỏ qua xác nhận, ≥8 ca dựa trên lời người dùng đã ẩn danh. Câu thử chính đi qua entry point nhận phiếu và câu hỏi đã xác nhận. Ca ảnh và mic có bảng kiểm riêng, không tính vào tỷ lệ 24 ca.
- [ ] **Chuẩn đạt đề xuất để xác nhận trước CP2.** 100% ca thiếu dữ kiện hoặc ngoài phạm vi đi đúng nhánh, 100% ca có giá trị và đơn vị hợp lệ được đối chiếu đúng theo đáp án, ít nhất 90% ca giải thích bám đúng dòng và dữ kiện trên phiếu. Ghi cách chấm và mẫu số theo từng metric, rồi khóa ngưỡng trong `spec.md` §7 và `eval/metric_spec.yaml`. N1 và N4 chấm chéo 5 đầu ra, mục tiêu khớp ≥4/5. Báo cả x/24 và kết quả từng metric.
- [ ] **Chạy lại được.** Trước CP2 chạy `python run.py` với JSON mẫu và AI giả. Trước CP3 chạy `python run.py check`, `python run.py eval --try` rồi `python run.py eval`. Điền pass theo tiêu chí và chạy `python run.py score eval/run-1.csv`. CP4 lặp lại trên cùng bộ câu, dùng tên file run đã sinh thực tế và giữ kết quả các lượt.
- [ ] **Chi phí.** N4 điền 3 persona, chạy `python run.py simulate --try` trước CP3 và chạy đủ ≥50 phiên seed cố định trước CP4, dùng tỷ lệ đạt lượt 2 của cùng model để tính chi phí/tác vụ thành công. Lập 3 kịch bản thấp, cơ sở, cao, so tối thiểu 2 mức model có giá và ngày xem. Nếu bộ mô phỏng chỉ chạy trên phiếu đã xác nhận, ghi rõ phạm vi đo, cộng riêng chi phí đọc ảnh theo usage và tỷ lệ dùng ảnh giả định, ghi thời gian chạy Zipformer cục bộ riêng. So chi phí/người/tháng với impact ghi nhận.
- [ ] **Demo.** Một ca tải ảnh giả lập → sửa/xác nhận → hỏi qua mic → thấy bản chép và giải thích. Một ca nhập tay thiếu đơn vị → app báo đúng trường cần bổ sung. Kiểm video 30 giây CP3, slide PDF có phần đánh giá và chi phí, video dự phòng CP4 và link mở được khi đăng xuất.
