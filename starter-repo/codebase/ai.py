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
import base64
import json
import os
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.request import Request
from urllib.parse import urlsplit

if __package__:
    from .tracing import model_call
    from .http_client import urlopen
else:
    from tracing import model_call
    from http_client import urlopen

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


def _api_origin(base: str):
    try:
        parsed = urlsplit(base)
        port = parsed.port
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError
        return parsed.hostname, port, parsed.scheme
    except ValueError:
        raise RuntimeError("LLM_API_BASE và VISION_API_BASE phải là URL HTTPS hợp lệ.") from None


@model_call
def call_model(system: str, user: str, *, output_schema: dict | None = None,
               images: list[bytes] | None = None, model_name: str | None = None,
               max_tokens: int | None = None,
               reasoning_effort: str | None = None) -> dict:
    if MODEL_PROVIDER == "fake":
        last = (user.strip().splitlines() or [""])[-1]
        return {"text": "[câu trả lời giả — chưa nối model] " + last[:60], "model": "fake", "tokens_in": 0, "tokens_out": 0}

    selected_model = model_name or MODEL_NAME
    if MODEL_PROVIDER not in ("ollama", "openai_compatible") or not selected_model:
        raise RuntimeError("Cấu hình MODEL_PROVIDER=ollama hoặc openai_compatible và MODEL_NAME.")

    if max_tokens is not None and (type(max_tokens) is not int or max_tokens <= 0):
        raise ValueError("max_tokens phải là số nguyên dương.")
    if reasoning_effort is not None and reasoning_effort not in ("low", "medium", "high"):
        raise ValueError("reasoning_effort phải là low, medium hoặc high.")
    user_message = {"role": "user", "content": user}
    if images is not None:
        if not isinstance(images, list) or any(not isinstance(item, bytes) or not item for item in images):
            raise ValueError("images phải là danh sách dữ liệu ảnh bytes không rỗng.")
        user_message["images"] = [base64.b64encode(item).decode("ascii") for item in images]

    body = {
        "model": selected_model,
        "messages": [{"role": "system", "content": system}, user_message],
        "stream": False,
        "format": output_schema or "json",
        "think": False,
        "options": {"temperature": 0, "num_predict": max_tokens or 180},
    }
    endpoint = "http://127.0.0.1:11434/api/chat"
    headers = {"Content-Type": "application/json"}
    if MODEL_PROVIDER == "openai_compatible":
        base = os.environ.get("LLM_API_BASE", "https://api.openai.com/v1").rstrip("/")
        api_key = os.environ.get("API_KEY", "").strip()
        if images:
            base = os.environ.get("VISION_API_BASE", "").strip().rstrip("/") or base
            vision_key = os.environ.get("VISION_API_KEY", "").strip()
            text_origin = _api_origin(os.environ.get("LLM_API_BASE", "https://api.openai.com/v1"))
            vision_origin = _api_origin(base)
            if vision_origin != text_origin and not vision_key:
                raise RuntimeError("Điền VISION_API_KEY riêng khi dùng nhà cung cấp đọc ảnh khác.")
            api_key = vision_key or api_key
        _api_origin(base)
        if not api_key:
            raise RuntimeError("Điền API_KEY trong .env để gọi model qua API.")
        endpoint = base + "/chat/completions"
        headers["Authorization"] = "Bearer " + api_key
        if images:
            user_message["content"] = [{"type": "text", "text": user}] + [
                {"type": "image_url", "image_url": {
                    "url": "data:" + ("image/png" if image.startswith(b"\x89PNG") else "image/jpeg")
                    + ";base64," + base64.b64encode(image).decode("ascii")
                }} for image in images
            ]
            user_message.pop("images", None)
        token_limit_field = (
            "max_completion_tokens"
            if selected_model.casefold().startswith(("gpt-5", "gpt-6", "o1", "o3", "o4"))
            else "max_tokens"
        )
        body = {
            "model": selected_model, "messages": body["messages"],
            token_limit_field: max_tokens or 180,
            "temperature": 0,
        }
        if reasoning_effort and selected_model.casefold().startswith("gemini-"):
            body["reasoning_effort"] = reasoning_effort
        if output_schema:
            body["response_format"] = {"type": "json_schema", "json_schema": {
                "name": "cbc_result", "schema": output_schema, "strict": False,
            }}
    request = Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urlopen(request, timeout=300 if images else 90) as response:
            data = json.load(response)
    except HTTPError as exc:
        raise RuntimeError(f"Dịch vụ AI trả HTTP {exc.code}. Kiểm tra model, khóa API và hạn mức.") from None
    except (json.JSONDecodeError, UnicodeError):
        raise RuntimeError("Dịch vụ AI trả JSON không hợp lệ.") from None
    except (URLError, TimeoutError, OSError, HTTPException, ValueError):
        raise RuntimeError("Không kết nối được dịch vụ AI hoặc model phản hồi quá thời gian.") from None

    try:
        if MODEL_PROVIDER == "openai_compatible":
            reply = data["choices"][0]["message"]["content"]
            tokens_in = data["usage"]["prompt_tokens"]
            tokens_out = data["usage"]["completion_tokens"]
        else:
            reply = data["message"]["content"]
            tokens_in = data["prompt_eval_count"]
            tokens_out = data["eval_count"]
    except (KeyError, TypeError, IndexError) as exc:
        raise RuntimeError("Phản hồi dịch vụ AI thiếu nội dung hoặc số token.") from exc
    if not isinstance(reply, str) or not reply.strip():
        raise RuntimeError("Ollama trả lời rỗng.")
    if any(type(count) is not int or count < 0 for count in (tokens_in, tokens_out)):
        raise RuntimeError("Phản hồi dịch vụ AI có số token không hợp lệ.")
    return {"text": reply, "model": data.get("model") or selected_model,
            "tokens_in": tokens_in, "tokens_out": tokens_out}
