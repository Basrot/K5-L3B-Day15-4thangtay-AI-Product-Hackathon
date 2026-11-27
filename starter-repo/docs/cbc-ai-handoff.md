# Bàn giao phần AI cho CP2

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
3. **Zipformer.** Chạy `python -m pip install -r requirements.txt`. Tải và giải nén gói Zipformer tiếng Việt 30M INT8 được dẫn trong [tài liệu sherpa-onnx](https://k2-fsa.github.io/sherpa/onnx/pretrained_models/offline-transducer/zipformer-transducer-models.html#sherpa-onnx-zipformer-vi-30m-int8-2026-02-09-vietnamese). Đặt `ZIPFORMER_MODEL_DIR` trong `.env` trỏ đến thư mục chứa ba tệp ONNX và `tokens.txt`. Dùng WAV PCM mono 16-bit, 8–48 kHz, tối đa 30 giây. Mẫu WAV trong gói model dùng để thử kết nối. Ghi thêm một câu riêng có “huyết sắc tố” để thử luồng demo.
4. **Kiểm thử tự động.** Chạy `python -m unittest discover -s tests -v`.

Hàm AI nhận dữ liệu có cấu trúc. Phần đọc ảnh và xác nhận kết quả thuộc giao diện của thành viên 4. Model chọn dòng và loại câu hỏi gợi ý. Mọi số, đơn vị, khoảng và trạng thái hiển thị đều lấy từ hàm đối chiếu. Phần giải thích chỉ dùng khoảng tham chiếu do người dùng xác nhận trên phiếu.

**Trạng thái kiểm thử giọng nói.** Windows Application Control chặn thư viện native của wheel sherpa-onnx. Backend ONNX bên dưới đã nhận dạng được WAV tiếng Việt mẫu trên chính máy này và chuyển bản chép đến Ollama thật. Màn hình thử mic đã được mở tại cổng 8501. Độ chính xác với giọng nói của người dùng cần kiểm qua micro thực tế.

### Thử giọng nói trên Windows với ONNX Runtime

Backend `onnx` chạy cùng model Zipformer tiếng Việt 30M INT8 qua ONNX Runtime. Màn hình `voice_demo.py` dùng phiếu giả lập cố định để kiểm luồng micro → bản chép → xác nhận câu hỏi → AI giải thích. Trên máy này đã chuẩn bị `.venv` và model trong `runtime/zipformer`.

Mở PowerShell trong `starter-repo` và chạy `./start-voice-demo.ps1`, sau đó mở [màn hình thử](http://127.0.0.1:8501). Cho trình duyệt dùng micro, ghi một câu ngắn như “Vì sao huyết sắc tố có dấu L?”, bấm Chuyển thành chữ, sửa bản chép nếu cần, xác nhận phiếu mẫu rồi bấm Hỏi AI. Ollama dùng `qwen3:4b` trên cổng 11434.

Trên máy khác, tạo `.venv` bằng Python 3.12, cài `pip install -r requirements-voice.txt`, giải nén model vào `runtime/zipformer` và tải model Ollama trước khi chạy script. Đặt `ZIPFORMER_BACKEND=onnx` để dùng backend tương thích này trong giao diện chính. Hàm `transcribe_wav` giữ cùng cách gọi, backend ONNX nhận WAV 16 kHz. Giữ chế độ ghi âm `sample_rate=16000`.

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

Đây là kho dữ liệu của bản demo cục bộ dùng phiếu giả lập. DB lưu phiếu có cấu trúc và câu hỏi dạng chữ. Các tệp ảnh và WAV được xử lý trong bộ nhớ của bên gọi. Giao diện giữ session_id theo từng người dùng. Nếu triển khai nhiều tài khoản trên mạng, cần lớp xác thực và quyền truy cập tương ứng trước khi dùng lịch sử phiên.
