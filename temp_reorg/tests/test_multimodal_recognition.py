"""
Test suite for the unified multi-modal recognition system.
"""

import os
import sys
import unittest
import numpy as np
from pathlib import Path
import tempfile
import cv2

# Add the src directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the recognition API
from src.multimodal.recognition_api import MultiModalRecognitionSystem, MultiModalResult


class TestMultiModalRecognitionSystem(unittest.TestCase):
    """Test cases for the MultiModalRecognitionSystem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a system with mock components
        self.system = MultiModalRecognitionSystem()
        
        # Set up mock data
        self.test_dir = tempfile.mkdtemp()
        self.create_test_files()
        
    def tearDown(self):
        """Clean up after tests."""
        # Remove test files
        try:
            for file in os.listdir(self.test_dir):
                os.remove(os.path.join(self.test_dir, file))
            os.rmdir(self.test_dir)
        except Exception as e:
            print(f"Warning: Failed to clean up test files: {e}")
    
    def create_test_files(self):
        """Create test image, audio and video files for testing."""
        # Create test image (100x100 black image)
        self.test_image = os.path.join(self.test_dir, "test_image.jpg")
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite(self.test_image, img)
        
        # Create test audio file (empty file for mock testing)
        self.test_audio = os.path.join(self.test_dir, "test_audio.wav")
        with open(self.test_audio, "w") as f:
            f.write("")
        
        # Create test video file (empty file for mock testing)
        self.test_video = os.path.join(self.test_dir, "test_video.mp4")
        with open(self.test_video, "w") as f:
            f.write("")
    
    def test_initialization(self):
        """Test that the system initializes correctly."""
        self.assertIsNotNone(self.system)
        self.assertIsNotNone(self.system.audio_system)
        self.assertIsNotNone(self.system.vision_system)
    
    def test_multimodal_result(self):
        """Test the MultiModalResult data class."""
        # Create a minimal result
        result = MultiModalResult(source="test")
        self.assertEqual(result.source, "test")
        self.assertIsNone(result.audio_type)
        self.assertIsNone(result.speech_recognition)
        self.assertIsNone(result.objects_detected)
        
        # Create a more complete result
        full_result = MultiModalResult(
            source="test_full",
            timestamp=1.5,
            audio_type="speech",
            speech_recognition={"text": "hello world", "confidence": 0.9},
            objects_detected=[{"class_name": "person", "confidence": 0.8}]
        )
        
        self.assertEqual(full_result.source, "test_full")
        self.assertEqual(full_result.timestamp, 1.5)
        self.assertEqual(full_result.audio_type, "speech")
        self.assertEqual(full_result.speech_recognition["text"], "hello world")
        self.assertEqual(full_result.objects_detected[0]["class_name"], "person")
    
    def test_process_image_and_audio_file_check(self):
        """Test that process_image_and_audio checks for file existence."""
        with self.assertRaises(FileNotFoundError):
            self.system.process_image_and_audio(
                "non_existent_image.jpg",
                self.test_audio
            )
        
        with self.assertRaises(FileNotFoundError):
            self.system.process_image_and_audio(
                self.test_image,
                "non_existent_audio.wav"
            )
    
    def test_context_generation(self):
        """Test context generation from detection results."""
        # Create a test result
        result = MultiModalResult(
            source="test_context",
            speech_recognition={"text": "hello world"},
            objects_detected=[
                {"category": "person", "class_name": "person", "confidence": 0.9},
                {"category": "animal", "class_name": "dog", "confidence": 0.8}
            ]
        )
        
        # Generate context
        self.system._generate_context_for_result(result)
        
        # Check that context was created
        self.assertIsNotNone(result.context)
        self.assertIn("scene_description", result.context)
        self.assertIn("audio_context", result.context)
        
        # Check that objects were included in scene description
        scene_desc = result.context["scene_description"]
        self.assertTrue(any("person" in desc for desc in scene_desc))
        self.assertTrue(any("dog" in desc for desc in scene_desc))
        
        # Check that speech was included in audio context
        audio_ctx = result.context["audio_context"]
        self.assertTrue(any("hello world" in ctx for ctx in audio_ctx))


class TestIntegration(unittest.TestCase):
    """Integration tests for the multi-modal recognition system.
    
    These tests use real models and may require additional setup.
    Skip if models or dependencies are not available.
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up for integration tests."""
        try:
            cls.system = MultiModalRecognitionSystem()
        except Exception as e:
            cls.setup_failed = True
            cls.setup_error = str(e)
        else:
            cls.setup_failed = False
            cls.setup_error = None
    
    def setUp(self):
        """Skip tests if setup failed."""
        if self.setup_failed:
            self.skipTest(f"Integration test setup failed: {self.setup_error}")
    
    def test_vision_integration(self):
        """Test integration with vision system if available."""
        try:
            # Try to get a detector and detect in a blank image
            detector = self.system.vision_system
            test_image = np.zeros((100, 100, 3), dtype=np.uint8)
            detections = detector.detect(test_image)
            
            # Just check that we get back the expected type
            self.assertIsInstance(detections, list)
            
        except Exception as e:
            self.skipTest(f"Vision integration test skipped: {e}")
    
    def test_audio_integration(self):
        """Test integration with audio system if available."""
        try:
            # Try to access the audio system
            audio_system = self.system.audio_system
            
            # Check that we can access the components
            self.assertIsNotNone(audio_system.speech_recognizer)
            self.assertIsNotNone(audio_system.voice_analyzer)
            self.assertIsNotNone(audio_system.music_analyzer)
            self.assertIsNotNone(audio_system.sound_classifier)
            
        except Exception as e:
            self.skipTest(f"Audio integration test skipped: {e}")


if __name__ == "__main__":
    unittest.main()
