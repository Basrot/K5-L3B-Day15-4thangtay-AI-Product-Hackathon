# DESIGN.md — Đọc phiếu CBC thai kỳ (4thangtay)

- **Phương án đã chọn:** Phương án A — Hai cột song hành (Desktop 12 cột: trái 5 cột Nhập & Xác nhận, phải 7 cột Đối chiếu & Hỏi đáp; Mobile xếp 1 cột responsive).
- **Bộ mặt:** Soft (nền `#eef2f3`, card `#ffffff` bo `12px`, bóng nhẹ `--elevation-card`, không viền nặng).
- **Màu nhấn:** Xanh ngọc y tế (`--primary: #0f766e`, `--primary-hover: #0d5e58`).
- **Font:** `Inter` (weight 400, 500, 600).
- **Trạng thái đối chiếu:** `below` (rose), `within` (emerald), `above` (amber).
- **Màn hình đã dựng:** `/` — Trang làm việc chính gồm đăng nhập demo, quản lý phiên, nhập tay / tải ảnh OCR, xác nhận phiếu (`study`/`lab`), bảng đối chiếu 8 chỉ số, hỏi đáp AI + ghi âm WAV 16 kHz + đọc giọng nói VieNeu.
