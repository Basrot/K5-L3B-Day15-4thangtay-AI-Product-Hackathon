# Bàn giao phần AI cho CP2

## Phạm vi mở rộng

Ứng dụng trong demo nhận 8 chỉ số CBC đã đề xuất: HGB, RBC, HCT, MCV, MCH, MCHC, WBC và PLT. Danh mục đầy đủ từ workbook vẫn có trong `codebase/catalog.py`, nhưng API và giao diện chỉ công bố 8 mã trong phạm vi demo.

Mở trang bằng `./start-voice-demo.ps1`. Có thể dùng phiếu giả lập 8 chỉ số, nhập phiếu mới, hoặc tải JPG/PNG rồi đọc vào các ô. Phiếu mới mặc định dùng “Nghiên cứu theo tam cá nguyệt”: chỉ nhập kết quả và đơn vị, xác nhận từ 18 tuổi, đang mang thai và điền tuổi thai lúc xét nghiệm. Backend chọn khoảng nghiên cứu tương ứng; không cần gõ giới hạn dưới/trên. Muốn dùng khoảng của phòng xét nghiệm thì chọn “Khoảng ghi trên phiếu” và kiểm đủ năm trường mỗi dòng. App trả bảng đối chiếu từng dòng, tóm tắt số dòng dưới/trong/trên khoảng và bản kết quả tải về. Khi sửa dữ liệu, tuổi thai hoặc nguồn khoảng, kết quả và xác nhận cũ được xóa, cần xác nhận lại.

Đọc ảnh dùng `extract_report(image_bytes, mime_type)` qua model thị giác đã cấu hình: API tương thích OpenAI hoặc Ollama cục bộ `gemma3:4b`. Có thể đổi `VISION_MODEL`; xem cấu hình nhà cung cấp trong `.env.example`. Trường không đọc được hoặc không có trên ảnh để trống để người dùng bổ sung, đặc biệt không tự điền đơn vị thiếu. OCR vẫn trả các khoảng in trên ảnh nhưng study bỏ qua chúng; lab chỉ dùng sau khi người dùng kiểm lại. Dùng `analyze_report(report)` để lấy bảng đối chiếu toàn phiếu sau xác nhận. Gọi `answer()` cho câu hỏi từng chỉ số hoặc yêu cầu tóm tắt.

File `data/full-panel-demo.json` là số dựng để kiểm phần mềm, gồm các khoảng dựng. Giao diện mặc định lấy kết quả/đơn vị của mẫu và bỏ qua khoảng dựng khi dùng study. Dữ liệu nghiên cứu gốc vẫn nằm ngoài repo. Khoảng study lấy từ bảng công bố của Pham et al. (2023), không tính lại từ các dòng dữ liệu riêng tư. Kết quả mang reference_mode, trimester, reference_source, reference_note; giao diện hiển thị nguồn và ghi chú cùng bảng, đưa cả vào bản tải xuống. reference_source có title và url tùy chọn; nguồn phiếu trong lab có thể chỉ có title, khi đó hiển thị tên nguồn và không tạo liên kết. Đây là khoảng nghiên cứu theo quần thể và phương pháp của bài báo, không phải ngưỡng chẩn đoán hoặc khoảng đã được xác nhận cho phòng xét nghiệm của người dùng. Giữ nguyên reference_note để trình bày các giới hạn áp dụng.

Ví dụ phiếu study tối thiểu:

```json
{
  "adult_confirmed": true,
  "pregnancy_status": "pregnant",
  "gestational_age": "21w3d",
  "reference_mode": "study",
  "rows": [{"analyte": "HGB", "value": "108", "unit": "g/L"}]
}
```

`reference_mode: "lab"` yêu cầu thêm ref_low/ref_high/ref_unit theo phiếu. Khi không có reference_mode, phiếu không có khoảng nào được xử lý theo study, phiếu có bất kỳ khoảng nào giữ lab; không trộn hai nguồn. Mở lại phiên cũ có khoảng không tự đổi sang study. Explicit study luôn bỏ qua khoảng gửi kèm. Quy ước tam cá nguyệt của demo giữ 28w6d ở nhóm 2 và chuyển sang nhóm 3 từ 29w0d. Frontend Vercel có thể xem trước nguồn/khoảng bằng endpoint có bearer token `/v1/references?gestational_age=21w3d`; xem [bàn giao API](frontend-api-handoff.md).

## Hai hàm dùng từ giao diện

Chạy từ thư mục chứa `run.py`. Truyền phiếu **sau khi người dùng đã xác nhận**. Dùng cùng định dạng [JSON mẫu](../data/cbc-demo-input.json) cho nhập tay, kết quả đọc ảnh và cột `input` của benchmark. Phiếu và khoảng tham chiếu trong JSON là dữ liệu giả lập.

```python
import json
from codebase.agent import answer
from codebase.speech import transcribe_wav

# Khi có WAV, điền bản chép vào ô hỏi và cho người dùng sửa.
transcript = transcribe_wav(wav_bytes)

# Khi người dùng gửi, dùng câu hỏi đã sửa và phiếu đã xác nhận.
result = answer(json.dumps({"report": report, "question": question}, ensure_ascii=False))
print(result["output"])
```

| Kết quả | Giao diện dùng thế nào |
|---|---|
| `explained` | Hiện `output`. `analyte` cho biết dòng được giải thích. |
| `needs_input` | Hiện trường cần bổ sung hoặc sửa. Giữ người dùng trong form. |
| `out_of_scope` | Hiện giới hạn đối tượng của bản demo. |
| `clarify_question` | Cho sửa câu hỏi. Khi đầu ra model không đọc được, app cũng dùng nhánh này. |
| `medical_advice`, `urgent` | Hiện hướng dẫn liên hệ nhân viên y tế từ `output`. |

`answer()` có thể báo lỗi cấu hình hoặc kết nối model bằng exception để khung đánh giá ghi lỗi. Giao diện bắt lỗi và cho thử lại. Nếu `transcribe_wav()` trả chuỗi rỗng hoặc báo lỗi, giữ ô hỏi cho phép gõ lại. Khi sửa bất kỳ trường nào của phiếu, giao diện yêu cầu xác nhận lại trước khi gọi `answer()`.

## Kiểm thử trên máy demo

1. **Chế độ giả CP2.** Giữ `MODEL_PROVIDER=fake` hoặc để trống trong `.env`. Chạy `python run.py` rồi dán JSON mẫu trên một dòng. Trên PowerShell có thể dùng:

   ```powershell
   $OutputEncoding = [System.Text.UTF8Encoding]::new()
   Get-Content -Raw -Encoding UTF8 data/cbc-demo-input.json | ConvertFrom-Json | ConvertTo-Json -Depth 6 -Compress | python run.py
   ```

   Kết quả mẫu có nhãn `[AI giả]`. HGB được quy đổi từ 108 g/L thành 10.8 g/dL và nằm dưới khoảng ghi trên phiếu mẫu.
2. **LLM thật.** Khởi động Ollama trên máy có model `qwen3:4b`. Đặt `MODEL_PROVIDER=ollama` và `MODEL_NAME=qwen3:4b` trong `.env`. Chạy lại ca trên và kiểm tên model, token vào/ra trong CLI. Ollama cục bộ dùng cổng mặc định 11434. Nên chạy sẵn một câu mẫu trước demo để model nạp xong.
3. **Zipformer.** Các Docker image API và demo tải Zipformer tiếng Việt 150M INT8 từ revision ghim trong Dockerfile; file `config.json` của model được dùng làm `tokens.txt`. Model card khai báo giấy phép `cc-by-nc-nd-4.0`. Để chạy trực tiếp ngoài Docker, cài `requirements-voice.txt`, tải đúng bốn artifact từ revision đó vào một thư mục và đặt `ZIPFORMER_MODEL_DIR` trỏ đến thư mục ấy. Dùng WAV PCM mono 16-bit, 8–48 kHz, tối đa 30 giây. Thử cả ba WAV mẫu và thêm câu riêng có “huyết sắc tố”.
4. **Kiểm thử tự động.** Chạy `python -m unittest discover -s tests -v`.

Hàm AI nhận dữ liệu có cấu trúc. Phần đọc ảnh và xác nhận kết quả thuộc giao diện của thành viên 4. Model chọn dòng và loại câu hỏi gợi ý. Mọi số, đơn vị, khoảng và trạng thái hiển thị đều lấy từ hàm đối chiếu. Phần giải thích dùng khoảng nghiên cứu đã chọn từ tuổi thai trong study hoặc khoảng do người dùng xác nhận trên phiếu trong lab, và nêu rõ nguồn.

**Trạng thái kiểm thử giọng nói.** Windows Application Control chặn thư viện native của wheel sherpa-onnx. Backend ONNX đã nhận dạng được cả ba WAV mẫu với bộ model 150M đã ghim; đây là smoke test tương thích, chưa phải đánh giá độ chính xác độc lập. Peak working set standalone khi nhận dạng cả ba WAV là khoảng 301 MiB trên Windows; đây không thay thế phép đo Docker/cgroup. Màn hình mic trên checkout gốc vẫn trỏ model 30M; cần cấu hình model 150M riêng và thử mic thực tế trước demo.

### Thử giọng nói trên Windows với ONNX Runtime

Backend `onnx` chạy Zipformer qua ONNX Runtime. Docker image đã cấu hình model 150M INT8; checkout Windows hiện có model 30M trong `runtime/zipformer`, nên chạy script trực tiếp trên máy đó vẫn dùng model 30M cho đến khi tải/cấu hình model 150M riêng. Màn hình `voice_demo.py` dùng phiếu giả lập cố định để kiểm luồng micro → bản chép → xác nhận câu hỏi → AI giải thích.

Mở PowerShell trong `starter-repo` và chạy `./start-voice-demo.ps1`, sau đó mở [màn hình thử](http://127.0.0.1:8501). Cho trình duyệt dùng micro, ghi một câu ngắn như “Vì sao huyết sắc tố có dấu L?”, bấm Chuyển thành chữ, sửa bản chép nếu cần, xác nhận phiếu mẫu rồi bấm Hỏi AI. Ollama dùng `qwen3:4b` trên cổng 11434.

Trên máy khác, tạo `.venv` bằng Python 3.12, cài `pip install -r requirements-voice.txt`, đặt bốn file model vào thư mục được `ZIPFORMER_MODEL_DIR` chỉ tới và tải model Ollama trước khi chạy script. Đặt `ZIPFORMER_BACKEND=onnx` để dùng backend tương thích này trong giao diện chính. Hàm `transcribe_wav` giữ cùng cách gọi, backend ONNX nhận WAV 16 kHz. Giữ chế độ ghi âm `sample_rate=16000`.

### Đọc câu trả lời bằng VieNeu

`codebase.tts.synthesize_wav(text) -> bytes` mặc định gọi API VieNeu chính thức qua HTTPS. Điền `VIENEU_API_KEY` trong `.env`, giữ `VIENEU_TTS_BACKEND=api`, `VIENEU_MODEL=vieneu-v4` và `VIENEU_VOICE=Minh Quân Pro`. Giọng này có tên hiển thị Hải Đăng trong danh mục API v4. Giao diện có ô “Đọc câu trả lời bằng giọng nói”. Khi tổng hợp thành công, trình phát xuất hiện bên dưới câu trả lời, có thể bấm nghe lại.

```python
from codebase.tts import synthesize_wav

wav_bytes = synthesize_wav(result["output"])
st.audio(wav_bytes, format="audio/wav", autoplay=True)
```

Hàm đổi tên 24 chỉ số, số thập phân và đơn vị sang cách đọc tiếng Việt. Khi tạo giọng gặp lỗi, giao diện vẫn hiện nội dung trả lời và thông báo lỗi âm thanh. API nhận phần giải thích cần đọc. Khóa được đọc ở phía server, còn trình duyệt nhận WAV.

Đường SDK cục bộ còn dùng được khi đặt `VIENEU_TTS_BACKEND=local` và cài `requirements-voice.txt`. Bản VPS dùng `requirements-server.txt`, cài các thư viện cần cho web và Zipformer. Trình duyệt có thể yêu cầu bấm Play để phát âm thanh. Các kiểm thử API dùng phản hồi WAV giả lập; cần khóa thật để xác minh tài khoản và hạn mức.

Giao thức được đối chiếu tại [OpenAPI VieNeu](https://docs.vieneu.io/openapi.json). Xem [cấu hình VPS](vps-deployment.md) để chạy LLM, đọc ảnh và giọng đọc qua API.

## SQLite và lịch sử phiên

Thành viên 4 dùng lớp dưới đây nếu cần lưu phiên khi tải lại giao diện. SQLite tự khởi tạo bảng và dùng thư viện chuẩn Python. Mặc định tạo `runtime/cbc.sqlite3` bên cạnh `run.py`, đã được bỏ qua trong Git. Khi thử tự động, truyền đường dẫn DB riêng.

```python
from codebase.service import CBCService

service = CBCService()
# Chỉ tạo một lần và giữ session_id trong trạng thái phiên của giao diện.
session_id = service.create_session()
revision = service.get_session(session_id)["revision"]
service.confirm_report(session_id, report, confirmed=True, expected_revision=revision)
# Giữ revision cùng phiếu được hiển thị và cùng lần gửi câu hỏi.
revision = service.get_session(session_id)["revision"]
result = service.ask(session_id, question, expected_revision=revision,
                     request_id="id-cua-lan-bam-gui")
messages = service.history(session_id)
saved_report = service.get_session(session_id)["report"]

# Gọi ngay khi người dùng sửa trường hoặc chọn ảnh khác.
service.invalidate_report(session_id, expected_revision=revision)
# Khi kết thúc hoặc người dùng xóa phiên.
service.delete_session(session_id)
```

Mỗi lần gửi dùng một request_id mới. Khi gửi lại cùng yêu cầu do tải lại trang hoặc lỗi mạng, giữ nguyên ID và expected_revision để lấy câu trả lời đã lưu. Tái sử dụng ID với câu hỏi khác báo ValueError. Hai yêu cầu đồng thời có cùng ID có thể cùng chạy model, nhưng chỉ một kết quả được lưu. Khi phiếu đổi trước hoặc trong lúc model trả lời, dịch vụ báo ValueError để giao diện tải lại dữ liệu và yêu cầu gửi lại.

`confirm_report` kiểm tra phiếu trước khi lưu, kiểm phiên bản, tăng revision và xóa lịch sử của phiếu trước. Xác nhận lại cùng dữ liệu giữ lịch sử hiện tại. `invalidate_report` kiểm phiên bản rồi xóa xác nhận và lịch sử. Các lần gọi model lỗi giữ nguyên dữ liệu đã xác nhận và cho phép thử lại. `delete_session` xóa cả phiếu và các câu hỏi trong một giao dịch. Giao diện có thể hiện `comparison` và `sources` trong kết quả `explained` để làm bảng đối chiếu và liên kết nguồn.

DB lưu phiếu có cấu trúc và câu hỏi dạng chữ. Các tệp ảnh và WAV được xử lý trong bộ nhớ của bên gọi. Giao diện giữ session_id theo từng người dùng và có mục “Phiên đã lưu” để mở lại bằng mã sau khi tải lại trang. “Nhập phiếu mới” mở phiên mới và xóa câu hỏi/bản ghi âm khỏi trạng thái đang xem. Phiếu trước vẫn nằm trong DB cho đến khi được xóa qua `delete_session`. Trên VPS, DB nằm trong volume Docker và bản demo dùng mật khẩu truy cập qua Caddy.
