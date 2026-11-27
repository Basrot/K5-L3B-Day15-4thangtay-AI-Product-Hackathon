# Triển khai VPS CPU bằng Docker Compose

Cấu hình này chạy Streamlit, Zipformer tiếng Việt 30M int8 qua ONNX Runtime và SQLite trên VPS. LLM, đọc ảnh phiếu và VieNeu TTS dùng API bên ngoài. Không cần GPU hoặc cài SDK VieNeu trên server. Đây là cấu hình để triển khai sau; chưa SSH hay triển khai tới VPS thật.

## Chuẩn bị

- VPS Linux có Docker Engine và plugin Docker Compose, truy cập Internet ra ngoài qua HTTPS.
- Tên miền trỏ A/AAAA tới VPS; mở cổng TCP 80/443 và UDP 443 nếu dùng HTTP/3. Không mở cổng 8501 ra Internet.
- Có thể bắt đầu thử một VPS 1 vCPU / 1 GB RAM cho nhóm nhỏ và đo lại theo số phiên thực tế. Phép thử Linux Docker trên máy phát triển với giới hạn container 1 CPU / 512 MB đã chạy được xác nhận phiếu 24 chỉ số, SQLite và WAV tiếng Việt qua Zipformer. Đỉnh bộ nhớ cgroup của phép thử khoảng 215 MiB, sau khi script thử kết thúc app dùng khoảng 52 MiB. Số đo bao gồm app và tiến trình kiểm thử, chưa gồm hệ điều hành VPS, Caddy, gọi API thật hoặc nhiều người đồng thời. Đây là số đo chức năng một phiên, chưa phải kiểm thử tải.

## Cấu hình API và tên miền

Từ thư mục `starter-repo` trên VPS:

```sh
cp .env.example .env
chmod 600 .env
```

Điền `.env` theo nhà cung cấp thực tế. Các khóa chính:

```dotenv
DOMAIN=cbc.example.com
MODEL_PROVIDER=openai_compatible
LLM_API_BASE=https://your-provider.example/v1
API_KEY=replace-with-your-key
MODEL_NAME=your-text-model
VISION_MODEL=your-vision-model
VIENEU_TTS_BACKEND=api
VIENEU_API_KEY=replace-with-your-vieneu-key
VIENEU_VOICE=Minh Quân Pro
VIENEU_MODEL=vieneu-v4
BASIC_AUTH_USER=nhom-cbc
BASIC_AUTH_HASH='paste-caddy-password-hash-here'
```

Nhà cung cấp LLM cần hỗ trợ API Chat Completions và `response_format=json_schema`. Model đọc ảnh phải hỗ trợ đầu vào hình ảnh. Nếu vision dùng endpoint hoặc tài khoản khác, đặt thêm `VISION_API_BASE` và `VISION_API_KEY` theo `.env.example`; khác host cần khóa riêng. Không commit `.env`. Compose truyền file này cho app. HTTPS hoạt động khi DNS và cổng mạng đã đúng; trình duyệt cần HTTPS để thu âm microphone.

Tạo hash mật khẩu truy cập bản demo bằng `docker run --rm -it caddy:2 caddy hash-password`. Dán hash vào `BASIC_AUTH_HASH` trong dấu nháy đơn như mẫu và đặt `BASIC_AUTH_USER`. Caddy yêu cầu tài khoản này trước khi cho vào app để kiểm soát việc sử dụng API trả phí. Caddy nhận tên miền, tên truy cập và hash, các khóa dịch vụ chỉ truyền cho app.

## Build và chạy

```sh
docker compose config --quiet
docker compose build --pull
docker compose up -d
docker compose ps
docker compose logs --tail=100 app caddy
```

Dockerfile dùng Python 3.12 slim Debian Bookworm, cài đúng bốn dependency trực tiếp trong `requirements-server.txt`. Bốn phiên bản đã được đối chiếu metadata của môi trường phát triển; tất cả hỗ trợ Python 3.12. Dependency bắc cầu vẫn do pip giải quyết lúc build.

Build tải archive chính thức [Zipformer tiếng Việt 30M int8](https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-zipformer-vi-30M-int8-2026-02-09.tar.bz2), chỉ giữ encoder/decoder/joiner và tokens trong image cuối. Build cần Internet; không tải model mỗi lần khởi động. `.dockerignore` chỉ cho phép mã ứng dụng, manifest và phiếu giả lập vào build context, loại trừ dataset gốc, `.env`, database và thư mục model cục bộ.

App chạy UID/GID 10001, lưu SQLite tại `/app/runtime/cbc.sqlite3` trên named volume `runtime`. Volume mới kế thừa quyền thư mục từ image. Nếu dùng volume cũ hoặc bind mount tự tạo, cấp quyền UID/GID 10001 cho thư mục trước khi chạy. Caddy giữ chứng chỉ trong volume riêng. Chỉ Caddy publish cổng host; app dùng mạng nội bộ Compose.

Upload giới hạn 10 MB/file, telemetry Streamlit tắt. `OMP_NUM_THREADS=1` và `OPENBLAS_NUM_THREADS=1` hạn chế các thư viện tương ứng; các thiết lập này không thay thế cấu hình thread riêng của ONNX Runtime. Theo dõi `docker stats` trong lúc nhập ảnh, ghi âm và chạy nhiều phiên; tăng RAM hoặc giảm số người dùng đồng thời nếu áp lực bộ nhớ tăng. Không đặt giới hạn RAM cứng trước khi có số đo thực tế.

## Kiểm tra sau khi chạy

Mở `https://<DOMAIN>`, đăng nhập bằng tài khoản demo, dùng phiếu giả lập, xác nhận phiếu và thử hỏi đáp. Thử tải ảnh rồi kiểm lại từng dòng trước khi xác nhận; thử microphone và nghe phản hồi. Kiểm tra cả ba kết nối API; healthcheck HTTP chỉ chứng minh Streamlit đáp ứng, không kiểm tra credentials hay khả năng gọi model. Giữ mã trong mục “Phiên đã lưu”. Sau `docker compose restart app`, dùng mã này mở lại phiếu đã xác nhận.

SQLite phù hợp một app instance trên một VPS; không scale nhiều app container dùng chung volume. Bản demo không có hệ thống đăng nhập hay chính sách lưu giữ hồ sơ hoàn chỉnh. Chỉ dùng dữ liệu giả lập trên endpoint công khai; trước khi đưa phiếu thật lên cần bảo vệ truy cập và thống nhất việc gửi ảnh/nội dung đến các API ngoài.

## Sao lưu, khôi phục và cập nhật

Sao lưu SQLite đang chạy bằng API backup, không chép riêng file `.sqlite3` trong khi có giao dịch:

```sh
docker compose exec -T app python -c 'import sqlite3; s=sqlite3.connect("/app/runtime/cbc.sqlite3"); d=sqlite3.connect("/app/runtime/backup.sqlite3"); s.backup(d); d.close(); s.close()'
docker compose cp app:/app/runtime/backup.sqlite3 ./cbc-backup.sqlite3
```

Giữ bản sao lưu ở nơi có kiểm soát truy cập. Để khôi phục, dừng app, chép backup vào volume dưới tên `cbc.sqlite3` với UID/GID 10001 và loại bỏ WAL/SHM cũ của database đã dừng; không ghi đè database đang chạy. Sao lưu thêm `.env` và volume Caddy bằng cơ chế backup riêng của VPS.

```sh
docker compose build --pull
docker compose up -d
docker compose ps
```

`docker compose down` giữ named volume. Tránh `docker compose down -v` vì lệnh đó xóa database và dữ liệu chứng chỉ. Trước lần cập nhật có thay đổi schema, tạo backup và giữ image trước đó để có thể quay lại.
