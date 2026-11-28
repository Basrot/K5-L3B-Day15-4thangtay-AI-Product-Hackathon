# Chạy ứng dụng CBC đầy đủ trên Windows

Ứng dụng web hiện tại gồm giao diện Next.js, API FastAPI và SQLite. `start-voice-demo.ps1` là màn hình Streamlit thử mic riêng, không khởi động ứng dụng web này.

## Điều kiện cần

- Python 3.12 (hoặc phiên bản Python được dự án hỗ trợ), Node.js LTS và npm.
- Ollama đã cài và đang chạy nếu muốn hỏi đáp/đọc ảnh bằng model local.
- Đã tải model một lần:

  ```powershell
  ollama pull qwen3:4b
  ollama pull gemma3:4b
  ```

## Cài đặt một lần

Mở PowerShell tại `starter-repo`:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-api.txt
Copy-Item .env.example .env
```

Mở `starter-repo\.env`. Đặt các biến sau để hỏi đáp và đọc ảnh bằng Ollama local:

```dotenv
MODEL_PROVIDER=ollama
MODEL_NAME=qwen3:4b
VISION_MODEL=gemma3:4b
APP_USERNAME=local-admin
APP_PASSWORD=thay-bang-mat-khau-local-cua-ban
APP_SECRET=thay-bang-chuoi-ngau-nhien-it-nhat-32-ky-tu
```

Tạo `APP_SECRET` bằng lệnh sau rồi chép giá trị vừa in vào `.env`:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(32))"
```

Không dùng placeholder nguyên văn cho mật khẩu hoặc secret. Chỉ cần `APP_SECRET` để đăng ký tài khoản; `APP_USERNAME` và `APP_PASSWORD` tạo tài khoản admin local để duyệt hồ sơ bác sĩ. Tệp `.env` không được commit. Không cần `API_KEY` OpenAI hoặc `VIENEU_API_KEY` cho hỏi đáp/đọc ảnh bằng Ollama.

## Khởi động

Giữ hai cửa sổ PowerShell riêng luôn mở.

**Cửa sổ 1 — backend**, tại `starter-repo`:

```powershell
.\.venv\Scripts\python.exe -m uvicorn codebase.api:app --host 127.0.0.1 --port 8000
```

Kiểm tra API tại `http://127.0.0.1:8000/health`; kết quả mong đợi là `{"status":"ok"}`. Mở `/` ở cổng 8000 sẽ trả 404 bình thường vì đây là API, không phải giao diện web.

**Cửa sổ 2 — giao diện**, tại `starter-repo`:

```powershell
Set-Location .\frontend
npm install
npm run dev
```

Mở `http://localhost:3000`. Sau lần `npm install` đầu tiên, các lần sau chỉ cần `npm run dev`. Không bấm `Ctrl+C` hoặc đóng cửa sổ khi đang dùng ứng dụng.

## Tài khoản, model và dữ liệu

- Đăng ký bằng email/mật khẩu hoạt động local khi backend có `APP_SECRET` dài ít nhất 32 ký tự. Mật khẩu đăng ký cần ít nhất 10 ký tự.
- Google login chỉ hiện khi cấu hình `NEXT_PUBLIC_GOOGLE_CLIENT_ID` cho Next.js và `GOOGLE_CLIENT_ID` cho backend, đồng thời cho phép origin `http://localhost:3000` trong Google OAuth.
- Tài khoản, phiếu và lịch sử local được lưu trong SQLite tại `runtime/cbc.sqlite3`; chúng tách biệt với Railway. Hãy đăng ký tài khoản local mới.
- `qwen3:4b` chạy hỏi đáp và `gemma3:4b` xử lý ảnh trên máy. Lần tải model cần Internet; sau khi tải, Ollama xử lý cục bộ. Độ chính xác của giải thích y khoa không được bảo đảm chỉ bằng việc chạy model local.
- Nút **Chọn ảnh / PDF** nhận JPG/PNG hoặc PDF không đặt mật khẩu, tối đa 10 MB và ba trang của cùng một phiếu. PDF được chuyển thành ảnh trong bộ nhớ rồi gửi model đọc ảnh; không tự xác nhận dữ liệu. Sau khi tải, kiểm tra các con số, đơn vị, tuổi thai và ngày lấy mẫu rồi mới xác nhận. Tải lỗi hoặc không tìm thấy chỉ số sẽ giữ dữ liệu cũ.
- Bản nháp OCR nhận bí danh rõ ràng như Hb/HGB và gộp các dòng trùng hoàn toàn. Nếu một chỉ số có kết quả, đơn vị hoặc khoảng đọc ra mâu thuẫn, dòng đó được để trống kèm cảnh báo; không tự chọn cột, lấy trung bình hay ghép các ô từ những dòng khác nhau. Những dòng hợp lệ còn lại vẫn có thể kiểm tra và dùng tiếp.
- Cần cài lại `requirements-api.txt` khi nâng cấp để có `pypdfium2`. Nếu dùng OpenAI, đặt `VISION_MODEL=gpt-4.1-mini` và `VISION_API_BASE=https://api.openai.com/v1`; mặc định dùng cùng `API_KEY` với hỏi đáp. Nếu để trống `VISION_MODEL`, backend thử dùng `MODEL_NAME`, nên model đó cần hỗ trợ ảnh.
- Hỏi về phiếu cá nhân sẽ nhận giải thích chi tiết hơn, khoảng 150–220 từ. Câu hỏi khái niệm ngắn hơn; thời gian chờ tăng theo độ dài câu trả lời, đặc biệt khi chạy model bằng CPU.
- Trợ lý xưng em, gọi chị và đón nhận việc hỏi lại. Khi chị bày tỏ lo lắng, lời giải thích ưu tiên từng ý nhỏ, công nhận cảm xúc và một bước tiếp theo; không hứa mẹ/bé an toàn từ riêng CBC, tự nhận là bác sĩ/người thật hoặc thay thế hỗ trợ từ người thân và nhân viên y tế.
- Giải thích do model tạo cần chọn mã nguồn có trong `codebase/evidence.py`. Nguồn được hiển thị cùng phạm vi nội dung mà nó hỗ trợ; nguồn chung không phải bằng chứng cho một lời khuyên riêng của người dùng. Thiếu mã nguồn, mã bịa hoặc khuyến cáo vượt phạm vi sẽ không được hiển thị như một lời giải thích đạt yêu cầu.
- Hiện chưa có quy tắc khuyến cáo ăn uống, lượng nước, thay đổi thuốc hoặc sắt cho từng cá nhân được thẩm định. Các câu hỏi này nhận lời giải thích giới hạn một cách nhẹ nhàng và gợi ý hỏi bác sĩ trực tiếp. Các nguồn chỉ phục vụ kiến thức chung; danh mục nguồn và bộ lọc chưa phải chứng nhận mọi câu sinh ra đúng về lâm sàng.
- Nhận dạng giọng nói cần `ZIPFORMER_BACKEND=onnx`, `ZIPFORMER_MODEL_DIR` trỏ đúng thư mục chứa `encoder.int8.onnx`, `decoder.onnx`, `joiner.int8.onnx` và `tokens.txt`. Chỉ tải Qwen/Gemma không cung cấp các file Zipformer này.
- VieNeu TTS local là tùy chọn riêng. Cài `vieneu==3.8.5` trong đúng `.venv` ở `starter-repo`, rồi đặt `VIENEU_TTS_BACKEND=local`. Nếu SDK chưa cài/nạp model được, tắt đọc giọng trong lúc thử các chức năng khác.

## Kiểm tra nhanh

Từ `starter-repo`, có thể chạy kiểm tra backend bằng:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Nếu đăng nhập/đăng ký báo lỗi, kiểm tra backend còn chạy và `APP_SECRET` đã được nạp. Nếu trang không mở, kiểm tra cửa sổ frontend còn hiện `Ready` và truy cập cổng 3000, không phải 8000.
