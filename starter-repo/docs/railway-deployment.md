# FastAPI trên Railway

Backend chạy bằng Docker CPU, một tiến trình Uvicorn. Zipformer tiếng Việt 150M INT8 chạy ONNX cục bộ; giải thích, đọc ảnh và tổng hợp giọng nói gọi API ngoài. Frontend Vercel gọi URL HTTPS của backend. Streamlit và Caddy không nằm trong image API.

Đây là hướng dẫn cấu hình để triển khai; việc chuẩn bị các file này không tạo dịch vụ Railway, không gửi API key và không xác nhận deployment đã hoạt động.

## 1. Tạo dịch vụ từ repository

Trong Railway, tạo service nối GitHub repository và chọn nhánh `main`. Đặt **Root Directory** là `/starter-repo`, **Railway Config File** là `/starter-repo/railway.toml`. Đường dẫn config tính từ gốc repository, độc lập với Root Directory. Xem [hướng dẫn monorepo chính thức](https://docs.railway.com/deployments/monorepo#deploying-an-isolated-monorepo).

File TOML chọn `DOCKERFILE`, `Dockerfile.api`, healthcheck `/health` và restart khi lỗi tối đa ba lần, theo [schema cấu hình Railway](https://docs.railway.com/config-as-code/reference). Giữ Start Command trống để dùng CMD của image: `python -m codebase.serve`. Launcher bind `0.0.0.0` và đọc `PORT` Railway cung cấp, mặc định local 8000. Không gán cứng cổng 8501; không bật nhiều worker hay nhiều replica khi đang dùng SQLite.

## 2. Gắn volume cho SQLite

Gắn một Railway volume vào đúng `/app/runtime` trước khi dùng dữ liệu cần giữ. Đặt:

```dotenv
CBC_DB_PATH=/app/runtime/cbc.sqlite3
RAILWAY_RUN_UID=0
```

Image mặc định chạy UID 10001. Railway volume được mount với quyền root; `RAILWAY_RUN_UID=0` là cách Railway hỗ trợ để tránh lỗi ghi volume cho image nonroot. Trên Railway cấu hình này chạy app bằng root trong container; không gắn Docker socket hay thư mục host. Tham khảo [giới hạn và quyền volume](https://docs.railway.com/volumes/reference#caveats). Nếu hạ tầng đã cấp quyền volume cho UID 10001, có thể bỏ biến override và kiểm tra app ghi database được trước khi sử dụng.

Database nằm trên volume; model nằm trong image tại `/opt/models/zipformer`, không chiếm quota volume. Không lưu SQLite trên filesystem tạm của deployment. Kiểm tra dung lượng volume thực tế trong project và theo dõi mức sử dụng; không coi quota storage là mức RAM ứng dụng cần. Volume và dịch vụ có thể tính phí theo gói đang dùng.

## 3. Khai báo biến và secrets

Nhập trong Railway **Variables**, không điền secrets vào GitHub hoặc frontend:

| Biến | Giá trị / ý nghĩa |
|---|---|
| `APP_USERNAME` | Ví dụ `demo` |
| `APP_PASSWORD` | Mật khẩu riêng, đủ mạnh; không dùng giá trị mẫu |
| `APP_SECRET` | Chuỗi ngẫu nhiên ít nhất 32 ký tự, dùng ký token |
| `GOOGLE_CLIENT_ID` | Tùy chọn; OAuth 2.0 Web Client ID để bật nút đăng nhập Google |
| `CORS_ORIGINS` | Các origin frontend chính xác, ngăn bằng dấu phẩy; ví dụ `https://your-app.vercel.app` |
| `MODEL_PROVIDER` | `openai_compatible` |
| `LLM_API_BASE` | Base URL API tương thích OpenAI, thường có `/v1` |
| `API_KEY` | Secret của nhà cung cấp LLM |
| `MODEL_NAME` | Mã model văn bản thực tế của nhà cung cấp |
| `VISION_MODEL` | Mã model hỗ trợ ảnh |
| `VISION_API_BASE`, `VISION_API_KEY` | Tùy chọn; để trống để dùng endpoint/key LLM |
| `VIENEU_TTS_BACKEND` | `api` |
| `VIENEU_API_KEY` | Secret VieNeu chính thức |
| `VIENEU_MODEL` | `vieneu-v4` |
| `VIENEU_VOICE` | `Minh Quân Pro` |
| `CBC_DB_PATH` | `/app/runtime/cbc.sqlite3` |
| `RAILWAY_RUN_UID` | `0` cho volume mặc định như giải thích ở trên |

Tạo `APP_SECRET` trên máy tin cậy bằng `python -c "import secrets; print(secrets.token_urlsafe(48))"` rồi nhập trực tiếp vào Railway. Giữ nguyên secret qua các deployment để token không bị vô hiệu ngoài dự kiến. Không chia sẻ nội dung Variables trong ảnh chụp hoặc logs.

Origin CORS gồm scheme và hostname, có port nếu dùng local; không có đường dẫn và dấu `/` cuối. Ví dụ cho hai frontend: `https://your-app.vercel.app,https://cbc.example.com`. Không dùng `*` hoặc wildcard preview domain. Mỗi preview frontend muốn kết nối phải được thêm origin cụ thể. Khi chạy local, thêm `http://localhost:3000` nếu đó là địa chỉ frontend thực tế.

Dockerfile ghim revision `8c3d474d3d74cb247f4b8c7b0f8b48598ac8c1c6` của [ZipFormer-150M-CR-CTC-RNNT-6000h](https://huggingface.co/hynt/ZipFormer-150M-CR-CTC-RNNT-6000h). Lúc build, tải encoder INT8, decoder, joiner INT8 và danh sách token (`config.json` của repo model được lưu thành `tokens.txt`); không tải checkpoint PyTorch hay các ONNX FP32. Model card ghi giấy phép `cc-by-nc-nd-4.0`; kiểm tra điều kiện giấy phép trước khi phát hành hoặc dùng cho mục đích thương mại. Dockerfile đặt `ZIPFORMER_BACKEND=onnx`, `ZIPFORMER_MODEL_DIR=/opt/models/zipformer`, `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`; tránh ghi đè thành giá trị rỗng từ cấu hình local. Backend dùng HTTP trực tiếp, không cần Streamlit, SDK VieNeu hay model LLM trên máy Railway.

## 4. Deploy và nối frontend

Sau khi volume và Variables đầy đủ, chạy deployment trong Railway. Theo dõi build logs: dependency CPU được cài từ `requirements-api.txt`; bốn file model đã ghim phiên bản được tải một lần lúc build và chỉ được giữ trong image cuối. Build context dùng allowlist `.dockerignore`, không đóng gói phiếu thật, database hoặc `.env`.

Khi deployment healthy, tạo Railway domain ở Networking. Railway kết thúc HTTPS; backend chỉ phục vụ HTTP nội bộ trên `$PORT`. Mở `https://<backend-domain>/health` để kiểm tra liveness. Healthcheck không kiểm tra credentials của nhà cung cấp AI.

Cung cấp frontend URL HTTPS công khai của backend; chỉ URL này được phép nằm trong biến frontend công khai. Mật khẩu, `APP_SECRET` và các API key ở backend. Sau khi biết domain Vercel cuối cùng, cập nhật `CORS_ORIGINS`, redeploy và thử login, nhập phiếu giả lập, phân tích, hỏi đáp, ảnh, microphone và TTS. Nếu gặp lỗi CORS, so sánh Origin trong request với giá trị đã nhập thay vì mở wildcard.

Đăng ký email/mật khẩu hoạt động ngay; email hiện chưa được xác minh và chưa có luồng quên mật khẩu. Để bật Google, tạo OAuth Client ID loại Web trong Google Cloud, thêm domain Vercel vào Authorized JavaScript origins, rồi đặt cùng Client ID vào Railway `GOOGLE_CLIENT_ID` và Vercel `NEXT_PUBLIC_GOOGLE_CLIENT_ID`; build lại frontend sau khi đổi biến Vercel. Không đưa client secret vào frontend. Backend xác minh Google ID token, issuer, audience và email đã xác minh trước khi tạo phiên đăng nhập. Tài khoản Google mới nhận quyền user; email đã đăng ký bằng mật khẩu không tự động được liên kết.

## 5. Kiểm tra vận hành và dữ liệu

Sau một lần restart/redeploy, xác nhận phiên đã lưu vẫn còn; nếu mất dữ liệu, kiểm tra mount path và `CBC_DB_PATH`. Lỗi `unable to open database file` hoặc `readonly database` thường cần kiểm tra quyền volume và `RAILWAY_RUN_UID`.

API image giảm dependency trực tiếp xuống FastAPI/Uvicorn/multipart/NumPy/ONNX Runtime/Pillow. Với model 150M, tiến trình Python standalone trên Windows đạt peak working set 315.682.816 byte (xấp xỉ 301 MiB) khi nạp model và nhận dạng ba WAV mẫu. Đây không phải phép đo cgroup/container: chưa đo RAM idle hoặc lúc xử lý âm thanh/ảnh đồng thời trong container giới hạn 512 MiB hay trên Railway. Hãy đo CPU/RAM với luồng thật trước khi chọn giới hạn bộ nhớ; kích thước model int8 không bằng toàn bộ RAM tiến trình. Một worker giúp tránh nạp model thành nhiều bản. Chưa xác nhận model 150M chạy ổn trong 512 MiB.

Lượt smoke test Docker ngày 27/11/2026 với model 30M trước đó: image build thành công; container 1 CPU/512 MiB nhận `PORT=8080`, xử lý luồng API và WAV mẫu; đỉnh cgroup 209.829.888 byte. Kết quả này chỉ là mốc tham khảo của 30M, không chứng minh image/model 150M vừa cấu hình cũng nằm trong 512 MiB. Docker chưa cài trong môi trường hiện tại nên cần build và đo lại image 150M trước demo. LLM/Vision/VieNeu qua tài khoản API thật và hạ tầng Railway cũng cần kiểm tra sau khi khai báo secrets. Các bài kiểm thử HTTP/mô hình trong suite dùng mocks cho dịch vụ ngoài.

Sao lưu SQLite bằng API `sqlite3.Connection.backup` hoặc snapshot nhất quán của volume; không chép riêng `.sqlite3` giữa giao dịch và bỏ qua WAL. Giữ backup ở nơi kiểm soát truy cập. Khi khôi phục, dừng tiến trình dùng DB rồi phục hồi cả trạng thái nhất quán; không ghi đè DB đang chạy. Kiểm tra quyền đọc/ghi lại sau khi restore.

Ứng dụng giữ tài khoản admin demo cấu hình qua môi trường và cho phép đăng ký user mới; mỗi tài khoản sở hữu các phiên CBC riêng. Tài khoản mới có thể dùng ngay, nhưng email chưa được xác minh; hiện chưa có đặt lại mật khẩu hay trang quản lý tài khoản. Dùng dữ liệu giả lập khi demo công khai; thống nhất bảo vệ truy cập, lưu giữ và việc chuyển dữ liệu tới các API ngoài trước khi dùng phiếu thật.
