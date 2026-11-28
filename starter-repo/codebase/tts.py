"""Đọc câu trả lời bằng API chính thức VieNeu, hoặc SDK local khi được chọn."""

import io
import json
import os
import re
import tempfile
import threading
import wave
from http.client import HTTPException
from functools import lru_cache
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request
from .http_client import urlopen
from .catalog import ANALYTES

_LOCK = threading.Lock()
MAX_AUDIO_BYTES = 20 * 1024 * 1024


def speech_text(text: str) -> str:
    """Đổi ký hiệu CBC sang cách đọc tiếng Việt trước khi tổng hợp."""
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\bTCN\s*([123])\b", r"tam cá nguyệt \1", text, flags=re.IGNORECASE)
    text = re.sub(r"\b([0-9]{1,2})w0d\b", r"\1 tuần", text, flags=re.IGNORECASE)
    text = re.sub(r"\b([0-9]{1,2})w([1-6])d\b", r"\1 tuần \2 ngày", text, flags=re.IGNORECASE)
    for code in sorted(ANALYTES, key=len, reverse=True):
        name = ANALYTES[code]
        text = re.sub(r"\b" + code + r"\b", name, text)
    text = re.sub(r"\bG/[Ll]\b", "nhân mười mũ chín trên lít", text)
    text = re.sub(r"\bT/[Ll]\b", "nhân mười mũ mười hai trên lít", text)
    text = text.replace("mg/dL", "mi li gam trên đề xi lít")
    text = text.replace("g/dL", "gam trên đề xi lít").replace("g/L", "gam trên lít")
    for unit in ("10⁹/L", "10^9/L"):
        text = text.replace(unit, "nhân mười mũ chín trên lít")
    for unit in ("10¹²/L", "10^12/L"):
        text = text.replace(unit, "nhân mười mũ mười hai trên lít")
    text = text.replace("10³/µL", "nghìn trên mi crô lít").replace("K/µL", "nghìn trên mi crô lít")
    text = text.replace("10⁶/µL", "triệu trên mi crô lít").replace("M/µL", "triệu trên mi crô lít")
    text = text.replace("L/L", "lít trên lít")
    text = text.replace("fL", "fem tô lít").replace("pg", "pi cô gam").replace("%", " phần trăm")
    text = re.sub(r"\bs\b", "giây", text)
    text = re.sub(r"(?<=\d)[.,](?=\d)", " phẩy ", text)
    return re.sub(r"(?<=\d)[–-](?=\d)", " đến ", text)


@lru_cache(maxsize=1)
def _engine():
    from vieneu import Vieneu

    return Vieneu(backend="onnx")


def _validate_wav(audio: bytes) -> bytes:
    """Reject empty, invalid and truncated PCM WAV responses before playback."""
    try:
        with wave.open(io.BytesIO(audio), "rb") as recording:
            channels, width = recording.getnchannels(), recording.getsampwidth()
            frame_count, rate = recording.getnframes(), recording.getframerate()
            if channels not in (1, 2) or width not in (1, 2, 3, 4) or frame_count <= 0 or not 8000 <= rate <= 192000:
                raise ValueError("invalid audio parameters")
            frames = recording.readframes(frame_count)
            if len(frames) != frame_count * channels * width:
                raise ValueError("truncated audio")
    except (wave.Error, EOFError, ValueError, OSError) as exc:
        raise RuntimeError("VieNeu trả âm thanh WAV rỗng hoặc không hợp lệ.") from exc
    return audio


def _api_wav(text: str) -> bytes:
    key = os.environ.get("VIENEU_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Thiếu VIENEU_API_KEY; thêm API key VieNeu vào file .env rồi khởi động lại ứng dụng.")
    body = {"input": text, "voice": os.environ.get("VIENEU_VOICE", "").strip() or "Minh Quân Pro",
            "model": os.environ.get("VIENEU_MODEL", "").strip() or "vieneu-v4", "response_format": "wav",
            "aiRefine": False, "applyPronunciation": False}
    request = Request("https://api.vieneu.io/api/v1/audio/speech", data=json.dumps(body).encode("utf-8"),
                      headers={"Content-Type": "application/json", "Accept": "audio/wav",
                               "Authorization": "Bearer " + key}, method="POST")
    try:
        with urlopen(request, timeout=90) as response:
            content_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
            if not (content_type.startswith("audio/") or content_type == "application/octet-stream"):
                raise RuntimeError("VieNeu không trả dữ liệu âm thanh WAV.")
            audio = response.read(MAX_AUDIO_BYTES + 1)
    except HTTPError as exc:
        raise RuntimeError(f"VieNeu API trả HTTP {exc.code}; kiểm tra API key, quyền giọng và hạn mức.") from None
    except (URLError, TimeoutError, OSError, HTTPException, ValueError) as exc:
        raise RuntimeError("Không kết nối được VieNeu API hoặc quá thời gian chờ.") from None
    if len(audio) > MAX_AUDIO_BYTES:
        raise RuntimeError("Âm thanh VieNeu vượt giới hạn 20 MB.")
    return _validate_wav(audio)


def _local_wav(text: str) -> bytes:
    with _LOCK:
        engine = _engine()
        audio = engine.infer(text, voice="Hải Đăng")
        with tempfile.TemporaryDirectory(prefix="cbc-vieneu-") as folder:
            output = Path(folder) / "reply.wav"
            engine.save(audio, str(output))
            return output.read_bytes()


def synthesize_wav(text: str) -> bytes:
    """Text → WAV; API by default, local SDK only for VIENEU_TTS_BACKEND=local."""
    if not isinstance(text, str) or not text.strip() or len(text) > 3000:
        raise ValueError("Nội dung đọc phải dài từ 1 đến 3000 ký tự.")
    backend = os.environ.get("VIENEU_TTS_BACKEND", "api").strip().lower()
    if backend not in ("api", "local"):
        raise RuntimeError("VIENEU_TTS_BACKEND phải là api hoặc local.")
    spoken = speech_text(text.strip())
    if backend == "api":
        return _api_wav(spoken)
    try:
        return _local_wav(spoken)
    except (ImportError, OSError, ValueError) as exc:
        raise RuntimeError("Không nạp hoặc chạy được VieNeu local; kiểm tra model và thư viện.") from None
