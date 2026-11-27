import unittest
from pathlib import Path


class StartVoiceDemoEncodingTest(unittest.TestCase):
    def test_script_has_utf8_bom_for_windows_powershell_5(self):
        script = Path(__file__).resolve().parents[1] / "start-voice-demo.ps1"
        self.assertTrue(script.read_bytes().startswith(b"\xef\xbb\xbf"))
