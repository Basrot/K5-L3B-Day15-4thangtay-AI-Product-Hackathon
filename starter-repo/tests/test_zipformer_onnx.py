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
