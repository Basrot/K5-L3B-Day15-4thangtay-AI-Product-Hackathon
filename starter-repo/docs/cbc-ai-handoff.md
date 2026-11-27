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

**Trạng thái kiểm thử giọng nói.** Các kiểm thử WAV tự động xác nhận đọc mẫu âm thanh, chuẩn hóa và chuyển dữ liệu đến bộ nhận dạng. Trên máy phát triển, Windows Application Control chặn thư viện native của wheel sherpa-onnx. Cần kiểm lại một WAV qua model thật trên máy demo hỗ trợ thư viện này.
