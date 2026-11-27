import unittest
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codebase.zipformer_onnx import log_mel


class FeaturesTest(unittest.TestCase):
    def test_one_second_has_one_hundred_frames_and_eighty_bins(self):
        features = log_mel(np.zeros(16000, dtype=np.float32))
        self.assertEqual(features.shape, (100, 80))
        self.assertTrue(np.isfinite(features).all())
        np.testing.assert_allclose(features, np.log(np.finfo(np.float32).eps), atol=1e-5)

    def test_tone_energy_is_localized_and_dc_offset_is_removed(self):
        tone = np.sin(np.arange(16000) * (2 * np.pi * 1000 / 16000)).astype(np.float32)
        plain = log_mel(tone)
        offset = log_mel(tone + 1)
        np.testing.assert_allclose(plain[:, 25:35], offset[:, 25:35], atol=0.01)
        self.assertGreater(plain[50].max() - plain[50].min(), 10)


class DockerModelConfigTest(unittest.TestCase):
    def test_api_and_demo_images_pin_the_same_150m_int8_files(self):
        repo = Path(__file__).resolve().parents[1]
        revision = "8c3d474d3d74cb247f4b8c7b0f8b48598ac8c1c6"
        expected_files = {
            "encoder-epoch-11-avg-2.int8.onnx": "encoder.int8.onnx",
            "decoder-epoch-11-avg-2.onnx": "decoder.onnx",
            "joiner-epoch-11-avg-2.int8.onnx": "joiner.int8.onnx",
            "config.json": "tokens.txt",
        }
        for name in ("Dockerfile.api", "Dockerfile"):
            with self.subTest(dockerfile=name):
                content = (repo / name).read_text(encoding="utf-8")
                self.assertIn(revision, content)
                self.assertIn("ARG ZIPFORMER_MODEL_REVISION=", content)
                self.assertIn('os.environ["ZIPFORMER_MODEL_REVISION"]', content)
                self.assertNotIn("30M-int8", content)
                for source, target in expected_files.items():
                    self.assertIn(f'"{source}": "{target}"', content)
