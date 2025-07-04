"""
Tests for the object detection module.
"""
import sys
from pathlib import Path

# Add mock modules to path if available
mock_path = Path(__file__).parent.parent / "src" / "mock_modules"
if mock_path.exists() and str(mock_path) not in sys.path:
    sys.path.insert(0, str(mock_path))


import unittest
import os
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock
try:
    import torch
except (ImportError, ModuleNotFoundError):
    print(f"Warning: torch module not available. Some functionality may be limited.")
    torch = None

try:
    import cv2
except (ImportError, ModuleNotFoundError):
    print(f"Warning: cv2 module not available. Some functionality may be limited.")
    cv2 = None


# Add the src directory to the Python path
import sys
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from vision.object_detection import (
    ObjectCategory,
    DetectionResult,
    ObjectDetector,
    YOLODetector,
    FaceDetector,
    get_detector
)

class TestObjectCategory(unittest.TestCase):
    """Tests for the ObjectCategory enum."""
    
    def test_enum_values(self):
        """Test that all expected categories are present."""
        expected_categories = [
            'FACE', 'ANIMAL', 'PLANT', 'INSECT', 'BIRD',
            'MECHANICAL', 'VEHICLE', 'FURNITURE', 'ELECTRONIC', 'UNKNOWN'
        ]
        
        for category in expected_categories:
            self.assertIn(category, ObjectCategory.__members__)
            self.assertEqual(ObjectCategory[category].value, category.lower())


class TestDetectionResult(unittest.TestCase):
    """Tests for the DetectionResult class."""
    
    def test_initialization(self):
        """Test that a DetectionResult is initialized correctly."""
        bbox = (10, 20, 100, 50)  # x, y, width, height
        result = DetectionResult(
            category=ObjectCategory.FACE,
            confidence=0.95,
            bbox=bbox,
            class_name="face",
            attributes={"key": "value"}
        )
        
        self.assertEqual(result.category, ObjectCategory.FACE)
        self.assertEqual(result.confidence, 0.95)
        self.assertEqual(result.bbox, bbox)
        self.assertEqual(result.class_name, "face")
        self.assertEqual(result.attributes, {"key": "value"})
    
    def test_default_attributes(self):
        """Test that attributes default to None if not provided."""
        result = DetectionResult(
            category=ObjectCategory.ANIMAL,
            confidence=0.8,
            bbox=(0, 0, 100, 100),
            class_name="dog"
        )
        
        self.assertIsNone(result.attributes)


class TestObjectDetectorBase(unittest.TestCase):
    """Base test class for object detectors with common setup."""
    
    @classmethod
    def setUpClass(cls):
        # Create a test image directory
        cls.test_dir = Path(__file__).parent / "test_images"
        cls.test_dir.mkdir(exist_ok=True)
        
        # Create a simple test image
        cls.test_image_path = cls.test_dir / "test.jpg"
        if not cls.test_image_path.exists():
            # Create a simple 100x100 red image
            img = np.zeros((100, 100, 3), dtype=np.uint8)
            img[:, :] = (0, 0, 255)  # Red in BGR
            cv2.imwrite(str(cls.test_image_path), img)
    
    @classmethod
    def tearDownClass(cls):
        # Clean up test files
        if cls.test_image_path.exists():
            cls.test_image_path.unlink()
        if cls.test_dir.exists():
            cls.test_dir.rmdir()


class TestYOLODetector(TestObjectDetectorBase):
    """Tests for the YOLODetector class."""
    
    def setUp(self):
        # Mock torch.hub.load to avoid downloading the actual model
        self.patcher = patch('torch.hub.load')
        self.mock_hub_load = self.patcher.start()
        
        # Create a mock model
        self.mock_model = MagicMock()
        self.mock_model.names = {
            0: 'person', 1: 'bicycle', 2: 'car', 3: 'dog', 16: 'bird'
        }
        self.mock_hub_load.return_value = self.mock_model
        
        # Mock model output
        self.mock_prediction = torch.tensor([
            [10, 20, 50, 80, 0.95, 0],    # person
            [30, 40, 80, 120, 0.85, 2],    # car
            [60, 70, 90, 110, 0.75, 3],    # dog
            [5, 5, 20, 20, 0.3, 16]        # bird (low confidence)
        ])
        self.mock_model.return_value.xyxy = [self.mock_prediction]
        
        # Initialize detector
        self.detector = YOLODetector()
    
    def tearDown(self):
        self.patcher.stop()
    
    def test_load_model(self):
        """Test that the model is loaded correctly."""
        # Model should be loaded in setUp
        self.assertIsNotNone(self.detector.model)
        self.mock_hub_load.assert_called_once()
    
    def test_detect_objects(self):
        """Test object detection with mock model."""
        # Call detect
        detections = self.detector.detect(str(self.test_image_path), confidence_threshold=0.5)
        
        # Should detect 3 objects (4th has low confidence)
        self.assertEqual(len(detections), 3)
        
        # Check first detection (person/face)
        self.assertEqual(detections[0].category, ObjectCategory.FACE)
        self.assertEqual(detections[0].class_name, "person")
        self.assertAlmostEqual(detections[0].confidence, 0.95)
        self.assertEqual(detections[0].bbox, (10, 20, 40, 60))  # x, y, w, h
        
        # Check second detection (car/mechanical)
        self.assertEqual(detections[1].category, ObjectCategory.MECHANICAL)
        self.assertEqual(detections[1].class_name, "car")
        
        # Check third detection (dog/animal)
        self.assertEqual(detections[2].category, ObjectCategory.ANIMAL)
        self.assertEqual(detections[2].class_name, "dog")
    
    def test_category_mapping(self):
        """Test the category mapping logic."""
        # Test face/person mapping
        self.assertEqual(
            self.detector._map_to_category("person"),
            ObjectCategory.FACE
        )
        
        # Test animal mapping
        self.assertEqual(
            self.detector._map_to_category("dog"),
            ObjectCategory.ANIMAL
        )
        
        # Test bird mapping
        self.assertEqual(
            self.detector._map_to_category("bird"),
            ObjectCategory.BIRD
        )
        
        # Test unknown mapping
        self.assertEqual(
            self.detector._map_to_category("unknown_class"),
            ObjectCategory.UNKNOWN
        )


class TestFaceDetector(TestObjectDetectorBase):
    """Tests for the FaceDetector class."""
    
    def setUp(self):
        # Mock cv2.dnn.readNetFromTensorflow
        self.patcher = patch('cv2.dnn.readNetFromTensorflow')
        self.mock_read_net = self.patcher.start()
        
        # Create a mock network
        self.mock_net = MagicMock()
        self.mock_read_net.return_value = self.mock_net
        
        # Mock network output
        self.mock_output = np.zeros((1, 1, 2, 7))  # 2 detections
        self.mock_output[0, 0, 0, 2] = 0.98  # confidence 1
        self.mock_output[0, 0, 0, 3:7] = [0.1, 0.2, 0.4, 0.5]  # bbox 1
        self.mock_output[0, 0, 1, 2] = 0.6   # confidence 2 (below threshold)
        
        self.mock_net.forward.return_value = self.mock_output
        
        # Initialize detector
        self.detector = FaceDetector()
    
    def tearDown(self):
        self.patcher.stop()
    
    def test_load_model(self):
        """Test that the face detection model is loaded correctly."""
        self.assertIsNotNone(self.detector.model)
        self.mock_read_net.assert_called_once()
    
    def test_detect_faces(self):
        """Test face detection with mock model."""
        # Call detect with a higher threshold
        detections = self.detector.detect(str(self.test_image_path), confidence_threshold=0.9)
        
        # Should detect 1 face (2nd detection has low confidence)
        self.assertEqual(len(detections), 1)
        
        # Check detection properties
        self.assertEqual(detections[0].category, ObjectCategory.FACE)
        self.assertEqual(detections[0].class_name, "face")
        self.assertAlmostEqual(detections[0].confidence, 0.98)
        
        # Check bbox (scaled from [0.1, 0.2, 0.4, 0.5] to image coords)
        # For a 100x100 image: x=10, y=20, w=30, h=30
        self.assertEqual(detections[0].bbox, (10, 20, 30, 30))


class TestDetectorFactory(unittest.TestCase):
    """Tests for the get_detector factory function."""
    
    @patch('vision.object_detection.YOLODetector')
    def test_get_yolo_detector(self, mock_yolo):
        """Test getting a YOLO detector instance."""
        detector = get_detector("yolo", model_path="custom.pt")
        mock_yolo.assert_called_once_with(model_path="custom.pt")
        self.assertEqual(detector, mock_yolo.return_value)
    
    @patch('vision.object_detection.FaceDetector')
    def test_get_face_detector(self, mock_face):
        """Test getting a face detector instance."""
        detector = get_detector("face", model_path="face_model.pb")
        mock_face.assert_called_once_with(model_path="face_model.pb")
        self.assertEqual(detector, mock_face.return_value)
    
    def test_invalid_detector_type(self):
        """Test that an invalid detector type raises an error."""
        with self.assertRaises(ValueError):
            get_detector("invalid_type")


if __name__ == "__main__":
    unittest.main()
