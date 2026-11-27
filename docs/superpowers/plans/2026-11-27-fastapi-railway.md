# Kế hoạch tách FastAPI cho Railway

Mục tiêu là đưa các chức năng hiện có ra HTTP API để frontend Vercel gọi trực tiếp. Giao diện Streamlit tiếp tục là công cụ thử cục bộ.

1. Tạo lớp đăng nhập bằng tài khoản demo, token HMAC có thời hạn và giới hạn kích thước request. CORS chỉ cho các origin được cấu hình.
2. Tạo FastAPI với health, danh mục, kiểm phiếu, phiên SQLite, xác nhận/hủy xác nhận, báo cáo, lịch sử, chat, trích xuất ảnh, nhận dạng WAV và tổng hợp WAV.
3. Giao dịch xác nhận và câu hỏi giữ expected_revision và request_id của dịch vụ hiện tại. Các tác vụ model dùng một khe xử lý để bảo toàn trace và RAM. Khi bận trả 429 để frontend chủ động thử lại.
4. Tạo Dockerfile API và Railway config, chạy một worker theo PORT, giữ DB trên /app/runtime. Bộ cài API bỏ Streamlit và SDK VieNeu, dùng LLM/Vision/VieNeu qua API.
5. Kiểm thử HTTP với DB tạm và mô hình giả ở ranh giới mạng, kiểm OpenAPI, build Docker, smoke test CPU. Viết hướng dẫn frontend gồm endpoint, payload, lỗi, CORS, bearer token và âm thanh.
6. Commit và đẩy main theo yêu cầu.

Các tệp chính gồm codebase/api.py, api_auth.py, api_limits.py, tests/test_api.py, tests/test_api_auth.py, Dockerfile.api, requirements-api.txt, railway.toml và docs/frontend-api-handoff.md.
