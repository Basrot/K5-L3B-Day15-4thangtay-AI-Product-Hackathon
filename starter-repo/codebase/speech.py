"""Chuyển WAV tiếng Việt thành văn bản bằng Zipformer cục bộ."""

import io
import os
import struct
import wave
from functools import lru_cache
from pathlib import Path

if __package__:
    from .ai import load_env
else:
    from ai import load_env

MAX_SECONDS = 30


@lru_cache(maxsize=1)
def _recognizer(model_dir: Path):
    files = {
        "encoder": model_dir / "encoder.int8.onnx",
        "decoder": model_dir / "decoder.onnx",
        "joiner": model_dir / "joiner.int8.onnx",
        "tokens": model_dir / "tokens.txt",
    }
    missing = [path.name for path in files.values() if not path.is_file()]
    if missing:
        raise RuntimeError("Thư mục Zipformer thiếu " + ", ".join(missing) + ".")
    try:
        from sherpa_onnx import OfflineRecognizer
    except ModuleNotFoundError as exc:
        if exc.name == "sherpa_onnx":
            raise RuntimeError("Cần cài sherpa-onnx để nhận dạng giọng nói.") from exc
        raise RuntimeError("Không nạp được phụ thuộc của sherpa-onnx.") from exc
    except (ImportError, OSError) as exc:
        raise RuntimeError(f"Không nạp được thư viện native của sherpa-onnx: {exc}") from exc
    return OfflineRecognizer.from_transducer(
        **{name: str(path) for name, path in files.items()},
        provider="cpu",
        num_threads=2,
    )


def transcribe_wav(wav_bytes: bytes) -> str:
    """Nhận WAV PCM mono 16-bit tối đa 30 giây, trả bản chép để người dùng sửa."""
    if not isinstance(wav_bytes, bytes):
        raise ValueError("Đầu vào phải là nội dung tệp WAV.")
    try:
        with wave.open(io.BytesIO(wav_bytes), "rb") as recording:
            rate = recording.getframerate()
            frames = recording.getnframes()
            if recording.getnchannels() != 1 or recording.getsampwidth() != 2:
                raise ValueError("Dùng WAV PCM mono 16-bit.")
            if not 8000 <= rate <= 48000 or frames > MAX_SECONDS * rate:
                raise ValueError("Dùng WAV 8–48 kHz, dài tối đa 30 giây.")
            raw = recording.readframes(frames)
    except (wave.Error, EOFError) as exc:
        raise ValueError("Không đọc được tệp WAV PCM.") from exc
    if len(raw) != frames * 2:
        raise ValueError("Tệp WAV thiếu dữ liệu âm thanh.")
    if not any(raw):
        return ""

    load_env()
    configured_dir = os.environ.get("ZIPFORMER_MODEL_DIR", "").strip()
    if not configured_dir:
        raise RuntimeError("Đặt ZIPFORMER_MODEL_DIR tới thư mục model Zipformer tiếng Việt.")
    model_dir = Path(configured_dir).expanduser()
    if not model_dir.is_absolute():
        model_dir = Path(__file__).resolve().parents[1] / model_dir
    samples = [sample / 32768 for (sample,) in struct.iter_unpack("<h", raw)]
    backend = os.environ.get("ZIPFORMER_BACKEND", "sherpa").strip().lower()
    if backend == "onnx":
        if __package__:
            from .zipformer_onnx import get_recognizer
        else:
            from zipformer_onnx import get_recognizer
        return get_recognizer(model_dir.resolve()).transcribe(samples, rate)
    if backend != "sherpa":
        raise ValueError("ZIPFORMER_BACKEND phải là sherpa hoặc onnx.")
    recognizer = _recognizer(model_dir.resolve())
    stream = recognizer.create_stream()
    stream.accept_waveform(rate, samples)
    recognizer.decode_stream(stream)
    return stream.result.text.strip()
