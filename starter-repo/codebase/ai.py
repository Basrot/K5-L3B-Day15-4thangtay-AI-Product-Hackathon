"""Nối model — chỗ DUY NHẤT trong bản chạy thử gọi model AI. NHÓM VIẾT phần gọi model thật.

Hợp đồng (giữ nguyên để khung đo được token):
    call_model(system: str, user: str) -> dict với 4 khoá
        "text":       str   chữ model trả về
        "model":      str   tên model đã gọi (để tra giá ở bảng giá model)
        "tokens_in":  int   số token vào, lấy từ trường usage trong phản hồi API — KHÔNG ước lượng
        "tokens_out": int   số token ra, gồm cả token suy luận / suy nghĩ nếu API tính riêng
    @model_call (từ tracing.py) tự ghi mỗi lần gọi vào trace; agent.py gọi call_model bao nhiêu lần
    cũng được, khung tự cộng token.
    Lỗi gọi model (hết lượt, sai key, mất mạng): cứ để exception bay ra — khung ghi lỗi vào cột error.

Chế độ giả (mặc định khi .env chưa có MODEL_PROVIDER, hoặc MODEL_PROVIDER=fake):
    trả một câu giả cố định, model "fake", token 0 — để luồng chạy hết từ trước CP2 (guide bước 3.2).
    Lượt `run.py eval` / `run.py simulate` chạy bằng model giả KHÔNG được tính.

Nối model thật: điền .env (chép từ .env.example), rồi viết nhánh gọi API ở dưới theo docs/connect-model.md
(có ví dụ OpenAI, Claude, model chạy trên máy, và cách nối nhà cung cấp khác). Không dán API key vào file này.
"""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

if __package__:
    from .tracing import model_call
else:
    from tracing import model_call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_env(path=os.path.join(ROOT, ".env")):
    """Đọc file .env (KEY=VALUE mỗi dòng) vào biến môi trường, không ghi đè biến đã có. Khung — không cần sửa."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()
MODEL_PROVIDER = (os.environ.get("MODEL_PROVIDER") or "fake").strip().lower()
MODEL_NAME = (os.environ.get("MODEL_NAME") or "").strip()


@model_call
def call_model(system: str, user: str, *, output_schema: dict | None = None) -> dict:
    if MODEL_PROVIDER == "fake":
        last = (user.strip().splitlines() or [""])[-1]
        return {"text": "[câu trả lời giả — chưa nối model] " + last[:60], "model": "fake", "tokens_in": 0, "tokens_out": 0}

    if MODEL_PROVIDER != "ollama" or not MODEL_NAME:
        raise ValueError("Cấu hình MODEL_PROVIDER=ollama và MODEL_NAME, hoặc dùng MODEL_PROVIDER=fake.")

    body = {
        "model": MODEL_NAME,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "stream": False,
        "format": output_schema or "json",
        "think": False,
        "options": {"temperature": 0, "num_predict": 180},
    }
    request = Request(
        "http://127.0.0.1:11434/api/chat",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=90) as response:
            data = json.load(response)
    except HTTPError as exc:
        raise RuntimeError(f"Ollama trả HTTP {exc.code}. Kiểm tra model đã tải và cấu hình.") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError("Không kết nối được Ollama cục bộ hoặc model phản hồi quá thời gian.") from exc

    try:
        reply = data["message"]["content"]
        tokens_in = data["prompt_eval_count"]
        tokens_out = data["eval_count"]
    except (KeyError, TypeError) as exc:
        raise RuntimeError("Phản hồi Ollama thiếu nội dung hoặc số token.") from exc
    if not isinstance(reply, str) or not reply.strip():
        raise RuntimeError("Ollama trả lời rỗng.")
    return {"text": reply, "model": data.get("model") or MODEL_NAME,
            "tokens_in": tokens_in, "tokens_out": tokens_out}
