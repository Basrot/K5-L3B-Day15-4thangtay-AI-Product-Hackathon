import sys
import io
import wave
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codebase.tts import synthesize_wav, speech_text


class TTSTest(unittest.TestCase):
    def test_cbc_symbols_are_spoken_as_vietnamese_words(self):
        self.assertEqual(speech_text("HGB 10.8 g/dL (11–14 g/dL)."),
                         "huyết sắc tố 10 phẩy 8 gam trên đề xi lít (11 đến 14 gam trên đề xi lít).")
        self.assertIn("bạch cầu", speech_text("WBC"))
        self.assertIn("tiểu cầu", speech_text("PLT"))

    def test_cell_count_units_keep_microliters_when_spoken(self):
        self.assertEqual(speech_text("WBC 5.2 10³/µL"),
                         "bạch cầu 5 phẩy 2 nghìn trên mi crô lít")
        self.assertEqual(speech_text("PLT 245 K/µL"),
                         "tiểu cầu 245 nghìn trên mi crô lít")

    def test_invalid_input_is_rejected_before_loading_model(self):
        with patch("codebase.tts._engine", side_effect=AssertionError("unexpected engine")):
            for text in ("", " " * 5, None, "a" * 3001):
                with self.subTest(text=str(text)[:20]), self.assertRaises(ValueError):
                    synthesize_wav(text)

    def test_returns_a_complete_playable_wav(self):
        class Engine:
            def infer(self, text, voice):
                return [0.0] * 4800

            def save(self, audio, path):
                with wave.open(str(path), "wb") as recording:
                    recording.setparams((1, 2, 48000, 0, "NONE", ""))
                    recording.writeframes(b"\x00\x00" * len(audio))

        with patch("codebase.tts._engine", return_value=Engine()):
            result = synthesize_wav("Xin chào.")
        with wave.open(io.BytesIO(result)) as recording:
            self.assertEqual(recording.getframerate(), 48000)
            self.assertEqual(recording.getnframes(), 4800)
