"""Đọc câu trả lời bằng giọng dựng sẵn của VieNeu chạy cục bộ."""

import re
import tempfile
import threading
from functools import lru_cache
from pathlib import Path

_LOCK = threading.Lock()


def speech_text(text: str) -> str:
    """Đổi ký hiệu CBC sang cách đọc tiếng Việt trước khi tổng hợp."""
    for code, name in (("HGB", "huyết sắc tố"), ("WBC", "bạch cầu"), ("PLT", "tiểu cầu")):
        text = re.sub(r"\b" + code + r"\b", name, text)
    text = text.replace("g/dL", "gam trên đề xi lít").replace("g/L", "gam trên lít")
    text = text.replace("10⁹/L", "nhân mười mũ chín trên lít")
    text = text.replace("10³/µL", "nghìn trên mi crô lít").replace("K/µL", "nghìn trên mi crô lít")
    text = re.sub(r"(?<=\d)[.,](?=\d)", " phẩy ", text)
    return re.sub(r"(?<=\d)[–-](?=\d)", " đến ", text)


@lru_cache(maxsize=1)
def _engine():
    from vieneu import Vieneu

    return Vieneu(backend="onnx")


def synthesize_wav(text: str) -> bytes:
    """Trả WAV bằng giọng Hải Đăng. Model được tải lúc gọi lần đầu."""
    if not isinstance(text, str) or not text.strip() or len(text) > 3000:
        raise ValueError("Nội dung đọc phải dài từ 1 đến 3000 ký tự.")
    with _LOCK:
        engine = _engine()
        audio = engine.infer(speech_text(text.strip()), voice="Hải Đăng")
        with tempfile.TemporaryDirectory(prefix="cbc-vieneu-") as folder:
            output = Path(folder) / "reply.wav"
            engine.save(audio, str(output))
            return output.read_bytes()
