"""
Object Detection Module

This module provides functionality for detecting and classifying objects in images
across multiple categories including faces, animals, plants, and mechanical objects.
"""

import cv2
import numpy as np
import torch
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ObjectCategory(Enum):
    """Enumeration of supported object categories."""
    FACE = "face"
    ANIMAL = "animal"
    PLANT = "plant"
    INSECT = "insect"
    BIRD = "bird"
    MECHANICAL = "mechanical"
    VEHICLE = "vehicle"
    FURNITURE = "furniture"
    ELECTRONIC = "electronic"
    UNKNOWN = "unknown"

@dataclass
class DetectionResult:
    """Data class to store detection results."""
    category: ObjectCategory
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    class_name: str
    attributes: Optional[Dict] = None

class ObjectDetector:
    """Base class for object detection models."""
    
    def __init__(self, model_path: Optional[str] = None, device: str = None):
        """Initialize the object detector.
        
        Args:
            model_path: Path to the model weights file.
            device: Device to run inference on ('cuda' or 'cpu').
        """
        self.model = None
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.classes = []
        self._load_model(model_path)
    
    def _load_model(self, model_path: Optional[str] = None):
        """Load the detection model.
        
        Args:
            model_path: Path to the model weights file.
        """
        raise NotImplementedError("Subclasses must implement _load_model")
    
    def detect(self, image: Union[str, np.ndarray], confidence_threshold: float = 0.5) -> List[DetectionResult]:
        """Detect objects in an image.
        
        Args:
            image: Path to the image or image array.
            confidence_threshold: Minimum confidence score for detections.
            
        Returns:
            List of DetectionResult objects.
        """
        raise NotImplementedError("Subclasses must implement detect")
    
    def _preprocess_image(self, image: Union[str, np.ndarray]) -> np.ndarray:
        """Preprocess the input image.
        
        Args:
            image: Path to the image or image array.
            
        Returns:
            Preprocessed image as a numpy array.
        """
        if isinstance(image, (str, Path)):
            image = cv2.imread(str(image))
            if image is None:
                raise ValueError(f"Could not read image: {image}")
        
        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image

class YOLODetector(ObjectDetector):
    """YOLO-based object detector."""
    
    def _load_model(self, model_path: Optional[str] = None):
        """Load YOLO model.
        
        Args:
            model_path: Path to the YOLO model weights file.
        """
        try:
            if model_path is None:
                # Load default YOLOv5 model
                self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
            else:
                # Load custom YOLO model
                self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)
            
            self.model.to(self.device)
            self.model.eval()
            
            # Get class names
            self.classes = self.model.names
            
            logger.info(f"Loaded YOLO model on device: {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise
    
    def detect(self, image: Union[str, np.ndarray], confidence_threshold: float = 0.5) -> List[DetectionResult]:
        """Detect objects using YOLO.
        
        Args:
            image: Path to the image or image array.
            confidence_threshold: Minimum confidence score for detections.
            
        Returns:
            List of DetectionResult objects.
        """
        try:
            # Preprocess image
            img = self._preprocess_image(image)
            
            # Run inference
            results = self.model([img])
            
            # Parse results
            detections = []
            for *xyxy, conf, cls_idx in results.xyxy[0]:
                confidence = float(conf)
                if confidence < confidence_threshold:
                    continue
                    
                # Convert coordinates to integers
                x1, y1, x2, y2 = map(int, xyxy)
                width = x2 - x1
                height = y2 - y1
                
                # Get class name
                class_idx = int(cls_idx)
                class_name = self.classes.get(class_idx, f"class_{class_idx}")
                
                # Map to our categories
                category = self._map_to_category(class_name)
                
                detections.append(DetectionResult(
                    category=category,
                    confidence=confidence,
                    bbox=(x1, y1, width, height),
                    class_name=class_name
                ))
            
            return detections
            
        except Exception as e:
            logger.error(f"Error during object detection: {e}")
            return []
    
    def _map_to_category(self, class_name: str) -> ObjectCategory:
        """Map YOLO class names to our categories."""
        class_name = class_name.lower()
        
        # Face detection
        if 'face' in class_name or 'person' in class_name:
            return ObjectCategory.FACE
        
        # Animals
        animals = ['dog', 'cat', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe']
        if any(animal in class_name for animal in animals):
            return ObjectCategory.ANIMAL
        
        # Birds
        birds = ['bird', 'eagle', 'hawk', 'owl', 'parrot', 'penguin']
        if any(bird in class_name for bird in birds):
            return ObjectCategory.BIRD
        
        # Insects
        insects = ['insect', 'bee', 'ant', 'butterfly', 'spider', 'mosquito']
        if any(insect in class_name for insect in insects):
            return ObjectCategory.INSECT
        
        # Plants
        plants = ['plant', 'tree', 'flower', 'bush', 'grass', 'potted plant']
        if any(plant in class_name for plant in plants):
            return ObjectCategory.PLANT
        
        # Mechanical objects
        mechanical = ['car', 'truck', 'bicycle', 'motorcycle', 'airplane', 'bus', 'train', 'boat']
        if any(m in class_name for m in mechanical):
            return ObjectCategory.MECHANICAL
        
        # Electronics
        electronics = ['cell phone', 'laptop', 'keyboard', 'mouse', 'tv', 'monitor']
        if any(e in class_name for e in electronics):
            return ObjectCategory.ELECTRONIC
        
        # Furniture
        furniture = ['chair', 'couch', 'bed', 'dining table', 'toilet', 'desk']
        if any(f in class_name for f in furniture):
            return ObjectCategory.FURNITURE
        
        return ObjectCategory.UNKNOWN

class FaceDetector(ObjectDetector):
    """Specialized face detector using OpenCV's DNN module."""
    
    def _load_model(self, model_path: Optional[str] = None):
        """Load face detection model."""
        try:
            # Load OpenCV's face detection model
            model_path = model_path or str(Path(__file__).parent / 'models/opencv_face_detector.pbtxt')
            weights_path = str(Path(__file__).parent / 'models/opencv_face_detector_uint8.pb')
            
            self.model = cv2.dnn.readNetFromTensorflow(weights_path, model_path)
            
            if self.device == 'cuda':
                self.model.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                self.model.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
            
            logger.info("Loaded face detection model")
            
        except Exception as e:
            logger.error(f"Failed to load face detection model: {e}")
            raise
    
    def detect(self, image: Union[str, np.ndarray], confidence_threshold: float = 0.7) -> List[DetectionResult]:
        """Detect faces in an image.
        
        Args:
            image: Path to the image or image array.
            confidence_threshold: Minimum confidence score for detections.
            
        Returns:
            List of DetectionResult objects.
        """
        try:
            # Preprocess image
            img = self._preprocess_image(image)
            h, w = img.shape[:2]
            
            # Prepare blob for the network
            blob = cv2.dnn.blobFromImage(
                img, 1.0, (300, 300), [104, 117, 123], 
                swapRB=False, crop=False
            )
            
            # Run inference
            self.model.setInput(blob)
            detections = self.model.forward()
            
            # Parse detections
            results = []
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                
                if confidence > confidence_threshold:
                    # Get bounding box coordinates
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    x1, y1, x2, y2 = box.astype('int')
                    width = x2 - x1
                    height = y2 - y1
                    
                    # Ensure coordinates are within image bounds
                    x1 = max(0, x1)
                    y1 = max(0, y1)
                    width = min(width, w - x1)
                    height = min(height, h - y1)
                    
                    results.append(DetectionResult(
                        category=ObjectCategory.FACE,
                        confidence=float(confidence),
                        bbox=(x1, y1, width, height),
                        class_name="face",
                        attributes={"detector": "OpenCV_DNN"}
                    ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error during face detection: {e}")
            return []

def get_detector(model_type: str = "yolo", **kwargs) -> ObjectDetector:
    """Factory function to get a detector instance.
    
    Args:
        model_type: Type of detector ('yolo' or 'face').
        **kwargs: Additional arguments to pass to the detector.
        
    Returns:
        An instance of the specified detector.
    """
    model_type = model_type.lower()
    if model_type == "yolo":
        return YOLODetector(**kwargs)
    elif model_type == "face":
        return FaceDetector(**kwargs)
    else:
        raise ValueError(f"Unsupported detector type: {model_type}")

# Example usage
if __name__ == "__main__":
    import argparse
    from PIL import Image, ImageDraw
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Object Detection Demo')
    parser.add_argument('image', type=str, help='Path to input image')
    parser.add_argument('--model', type=str, default='yolo', 
                        choices=['yolo', 'face'], 
                        help='Detection model to use')
    parser.add_argument('--confidence', type=float, default=0.5,
                        help='Minimum confidence threshold')
    parser.add_argument('--output', type=str, default='output.jpg',
                        help='Path to save output image')
    args = parser.parse_args()
    
    # Initialize detector
    detector = get_detector(args.model)
    
    # Detect objects
    detections = detector.detect(args.image, args.confidence)
    
    # Load image for visualization
    image = Image.open(args.image).convert("RGB")
    draw = ImageDraw.Draw(image)
    
    # Draw bounding boxes
    for det in detections:
        x, y, w, h = det.bbox
        
        # Draw rectangle
        draw.rectangle([x, y, x + w, y + h], outline="red", width=2)
        
        # Draw label
        label = f"{det.class_name} ({det.confidence:.2f})"
        draw.text((x, y - 10), label, fill="red")
    
    # Save output
    image.save(args.output)
    print(f"Detected {len(detections)} objects. Output saved to {args.output}")
    
    # Print detection summary
    print("\nDetection Summary:")
    print("-" * 40)
    print(f"{'Category':<15} {'Class':<20} {'Confidence':<10} {'Bounding Box'}")
    print("-" * 40)
    for det in detections:
        print(f"{det.category.value:<15} {det.class_name:<20} {det.confidence:<10.2f} {det.bbox}")
