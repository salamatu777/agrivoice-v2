import unittest
try:
    import numpy as np
    HAVE_NUMPY = True
except ImportError:
    HAVE_NUMPY = False

try:
    from app.voice_pipeline import VoicePipeline
    HAVE_PIPELINE = True
except ImportError:
    HAVE_PIPELINE = False

class TestVoicePipeline(unittest.TestCase):
    def setUp(self):
        if HAVE_PIPELINE:
            self.pipeline = VoicePipeline()

    def test_mock_transcription(self):
        if not HAVE_PIPELINE:
            self.skipTest("Torch/Transformers pipeline dependencies not installed in local environment")
        if HAVE_NUMPY:
            dummy_audio = np.zeros(16000, dtype=np.float32)
        else:
            dummy_audio = [0.0] * 16000
        
        result = self.pipeline.process_audio(dummy_audio, 16000)
        
        self.assertIn("transcript", result)
        self.assertIn("advice", result)
        self.assertIn("language", result)

if __name__ == '__main__':
    unittest.main()
