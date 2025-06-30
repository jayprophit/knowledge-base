"""
Test suite for the sound classification module.
"""

import os
import sys
import unittest
import numpy as np
from pathlib import Path

# Add the src directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.audio.sound_classification import SoundClassifier, SoundClassificationResult


class TestSoundClassifier(unittest.TestCase):
    """Test cases for the SoundClassifier class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.classifier = SoundClassifier()
        
        # Create a mock audio sample (1 second of white noise)
        sample_rate = 22050
        self.mock_audio = np.random.uniform(-1, 1, sample_rate)
        
    def test_init(self):
        """Test that the classifier initializes correctly."""
        self.assertIsNotNone(self.classifier)
        self.assertEqual(self.classifier.sample_rate, 22050)
        self.assertEqual(self.classifier.hop_length, 512)
        self.assertEqual(self.classifier.n_fft, 2048)
        
    def test_load_audio_from_array(self):
        """Test loading audio from a numpy array."""
        audio = self.classifier.load_audio(self.mock_audio)
        self.assertIsInstance(audio, np.ndarray)
        self.assertEqual(len(audio), len(self.mock_audio))
        
    def test_load_audio_with_duration(self):
        """Test loading audio with a specified duration."""
        # Create a 3-second audio sample
        sample_rate = 22050
        long_audio = np.random.uniform(-1, 1, 3 * sample_rate)
        
        # Load only 1 second
        audio = self.classifier.load_audio(long_audio, duration=1.0)
        self.assertEqual(len(audio), sample_rate)
        
    def test_extract_features(self):
        """Test feature extraction from audio."""
        features = self.classifier.extract_features(self.mock_audio)
        
        # We should have 40 MFCC features (mean, std, max, min) + 5 other features
        expected_size = 40 * 4 + 5
        self.assertEqual(len(features), expected_size)
        
    def test_get_sound_category(self):
        """Test the sound categorization function."""
        self.assertEqual(self.classifier._get_sound_category("dog_bark"), "animal")
        self.assertEqual(self.classifier._get_sound_category("car_horn"), "urban")
        self.assertEqual(self.classifier._get_sound_category("cough"), "human")
        self.assertEqual(self.classifier._get_sound_category("rain"), "nature")
        self.assertEqual(self.classifier._get_sound_category("unknown_sound"), "unknown")
        
    def test_classify_sound_without_model(self):
        """Test that classify_sound raises an error when no model is loaded."""
        with self.assertRaises(ValueError):
            self.classifier.classify_sound(self.mock_audio)
            
    def test_detect_sound_events(self):
        """Test the sound event detection."""
        # Skip this test if no model is loaded
        if self.classifier.model is None:
            self.skipTest("No model loaded, skipping event detection test")
            
        # Create a mock 5-second audio sample
        sample_rate = 22050
        long_audio = np.random.uniform(-1, 1, 5 * sample_rate)
        
        # Mock the classify_sound method to return predictable results
        original_classify_sound = self.classifier.classify_sound
        
        def mock_classify_sound(audio, duration=None, top_k=3):
            # Return a dummy result
            return SoundClassificationResult(
                label="test_sound",
                confidence=0.8,
                category="test",
                top_predictions=[{"label": "test_sound", "confidence": 0.8}]
            )
            
        try:
            self.classifier.classify_sound = mock_classify_sound
            events = self.classifier.detect_sound_events(
                long_audio, 
                window_size=1.0,
                hop_size=0.5,
                threshold=0.5
            )
            # We should have events detected at 0.0s, 0.5s, 1.0s, etc.
            self.assertGreater(len(events), 0)
            
        finally:
            # Restore the original method
            self.classifier.classify_sound = original_classify_sound


class TestSoundClassificationResult(unittest.TestCase):
    """Test cases for the SoundClassificationResult class."""
    
    def test_create_result(self):
        """Test creating a classification result."""
        result = SoundClassificationResult(
            label="dog_bark",
            confidence=0.85,
            category="animal",
            top_predictions=[
                {"label": "dog_bark", "confidence": 0.85},
                {"label": "children_playing", "confidence": 0.10}
            ],
            source_file="test.wav",
            duration=5.0,
            timestamp=2.5
        )
        
        self.assertEqual(result.label, "dog_bark")
        self.assertEqual(result.confidence, 0.85)
        self.assertEqual(result.category, "animal")
        self.assertEqual(len(result.top_predictions), 2)
        self.assertEqual(result.source_file, "test.wav")
        self.assertEqual(result.duration, 5.0)
        self.assertEqual(result.timestamp, 2.5)


if __name__ == "__main__":
    unittest.main()
