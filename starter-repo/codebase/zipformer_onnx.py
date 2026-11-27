"""Zipformer tiếng Việt 30M qua ONNX Runtime và log-mel bằng NumPy.

Thiết lập đặc trưng theo Kaldi: 25 ms / 10 ms, Povey, 80 mel, 20–7600 Hz,
snip_edges=false, dither=0. Decoder dùng greedy search một token mỗi frame.
Tham khảo kiến trúc tại https://github.com/k2-fsa/icefall/tree/master/egs/librispeech/ASR/zipformer
"""

from functools import lru_cache

import numpy as np


def log_mel(samples):
    """Nhận waveform chuẩn hóa 16 kHz, trả ma trận log-mel float32."""
    samples = np.asarray(samples, dtype=np.float32)
    count = (len(samples) + 80) // 160
    starts = np.arange(count)[:, None] * 160 - 120
    indices = starts + np.arange(400)
    # Kaldi phản chiếu biên, có lặp mẫu đầu và cuối.
    padded = np.pad(samples, (400, 400), mode="symmetric")
    frames = padded[indices + 400].copy()
    frames -= frames.mean(axis=1, keepdims=True)
    frames[:, 1:] -= 0.97 * frames[:, :-1].copy()
    frames[:, 0] *= 0.03
    frames *= np.hanning(400).astype(np.float32) ** 0.85
    power = np.abs(np.fft.rfft(frames, n=512))[:, :256] ** 2
    mel_frequencies = 1127 * np.log1p(np.arange(256) * 16000 / (512 * 700))
    edges = np.linspace(1127 * np.log1p(20 / 700), 1127 * np.log1p(7600 / 700), 82)
    rising = (mel_frequencies[None, :] - edges[:-2, None]) / (edges[1:-1] - edges[:-2])[:, None]
    falling = (edges[2:, None] - mel_frequencies[None, :]) / (edges[2:] - edges[1:-1])[:, None]
    weights = np.maximum(0, np.minimum(rising, falling))
    energies = power @ weights.T
    return np.log(np.maximum(energies, np.finfo(np.float32).eps)).astype(np.float32)


class ZipformerOnnx:
    def __init__(self, model_dir):
        import onnxruntime as ort

        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 1
        opts.inter_op_num_threads = 1
        self.encoder = ort.InferenceSession(str(model_dir / "encoder.int8.onnx"), opts,
                                           providers=["CPUExecutionProvider"])
        self.decoder = ort.InferenceSession(str(model_dir / "decoder.onnx"), opts,
                                           providers=["CPUExecutionProvider"])
        self.joiner = ort.InferenceSession(str(model_dir / "joiner.int8.onnx"), opts,
                                          providers=["CPUExecutionProvider"])
        self.context_size = int(self.decoder.get_modelmeta().custom_metadata_map["context_size"])
        self.tokens = {}
        for line in (model_dir / "tokens.txt").read_text(encoding="utf-8").splitlines():
            token, index = line.rsplit(maxsplit=1)
            self.tokens[int(index)] = token
        self.blank = next(index for index, token in self.tokens.items() if token == "<blk>")
        self.unknown = next((index for index, token in self.tokens.items() if token == "<unk>"), -1)

    def transcribe(self, samples, sample_rate):
        if sample_rate != 16000:
            raise ValueError("Backend ONNX dùng WAV 16 kHz. Đặt sample_rate=16000 khi ghi âm.")
        features = log_mel(samples)
        if len(features) < 20:
            return ""
        encoded, lengths = self.encoder.run(None, {
            "x": features[None], "x_lens": np.array([len(features)], dtype=np.int64),
        })
        history = [self.blank] * self.context_size
        decoded = self.decoder.run(None, {"y": np.array([history], dtype=np.int64)})[0].reshape(1, -1)
        for frame in encoded[0, :int(lengths[0])]:
            logits = self.joiner.run(None, {
                "encoder_out": frame.reshape(1, -1), "decoder_out": decoded,
            })[0]
            token = int(np.argmax(logits))
            if token not in (self.blank, self.unknown):
                history.append(token)
                context = np.array([history[-self.context_size:]], dtype=np.int64)
                decoded = self.decoder.run(None, {"y": context})[0].reshape(1, -1)
        return "".join(self.tokens[token] for token in history[self.context_size:]).replace("▁", " ").strip()


@lru_cache(maxsize=1)
def get_recognizer(model_dir):
    return ZipformerOnnx(model_dir)
