# Computer Vision Module

This module provides computer vision capabilities including object detection, face detection, and image classification across multiple categories.

## Features

- **Multi-category Object Detection**: Detect and classify objects across various categories including faces, animals, plants, insects, birds, and mechanical objects.
- **Face Detection**: Specialized face detection with high accuracy.
- **Extensible Architecture**: Easy to add new detection models and categories.
- **GPU Acceleration**: Supports CUDA for faster inference on compatible hardware.

## Installation

1. Install the required dependencies:

```bash
pip install torch torchvision opencv-python-headless numpy
```

2. For GPU acceleration (optional but recommended):

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118  # CUDA 11.8
```

## Quick Start

### Basic Object Detection

```python
from vision.object_detection import get_detector
from PIL import Image

# Initialize the detector (defaults to YOLOv5s)
detector = get_detector("yolo")

# Detect objects in an image
detections = detector.detect("path/to/image.jpg")

# Print detections
for det in detections:
    print(f"Detected {det.class_name} ({det.category.value}) with confidence {det.confidence:.2f}")
    print(f"  Bounding box: {det.bbox}")

# Visualize results
image = Image.open("path/to/image.jpg")
draw = ImageDraw.Draw(image)

for det in detections:
    x, y, w, h = det.bbox
    draw.rectangle([x, y, x + w, y + h], outline="red", width=2)
    label = f"{det.class_name} ({det.confidence:.2f})"
    draw.text((x, y - 10), label, fill="red")

image.save("output.jpg")
```

### Face Detection

```python
from vision.object_detection import get_detector

# Initialize the face detector
face_detector = get_detector("face")

# Detect faces in an image
faces = face_detector.detect("path/to/portrait.jpg")

print(f"Detected {len(faces)} faces")
```

## API Reference

### `get_detector(model_type, **kwargs)`

Factory function to get a detector instance.

**Parameters:**
- `model_type` (str): Type of detector ('yolo' or 'face').
- `**kwargs`: Additional arguments passed to the detector constructor.

**Returns:**
- An instance of the specified detector.

### `ObjectDetector` (Base Class)

Base class for all object detectors.

#### Methods:

- `detect(image, confidence_threshold=0.5)`: Detect objects in an image.
  - `image`: Path to image or image array.
  - `confidence_threshold`: Minimum confidence score for detections.
  - Returns: List of `DetectionResult` objects.

### `DetectionResult`

Data class containing detection results.

**Attributes:**
- `category` (ObjectCategory): Detected object category.
- `confidence` (float): Detection confidence score (0-1).
- `bbox` (tuple): Bounding box (x, y, width, height).
- `class_name` (str): Detected class name.
- `attributes` (dict, optional): Additional detection attributes.

### `ObjectCategory` (Enum)

Supported object categories:
- `FACE`: Human faces
- `ANIMAL`: Animals
- `PLANT`: Plants and vegetation
- `INSECT`: Insects and small creatures
- `BIRD`: Birds
- `MECHANICAL`: Mechanical devices and vehicles
- `VEHICLE`: Transportation vehicles
- `FURNITURE`: Furniture items
- `ELECTRONIC`: Electronic devices
- `UNKNOWN`: Unrecognized objects

## Advanced Usage

### Custom Model Paths

```python
# Load custom YOLO model
yolo_detector = get_detector(
    "yolo",
    model_path="path/to/custom.pt"
)

# Load custom face detection model
face_detector = get_detector(
    "face",
    model_path="path/to/face_detector.pbtxt",
    weights_path="path/to/face_detector.pb"
)
```

### Using GPU

```python
import torch

# Check if CUDA is available
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Initialize detector with specified device
detector = get_detector("yolo", device=device)
```

## Examples

### Object Detection on Webcam Feed

```python
import cv2
from vision.object_detection import get_detector

# Initialize detector
detector = get_detector("yolo")

# Open webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Detect objects
    detections = detector.detect(frame)
    
    # Draw detections
    for det in detections:
        x, y, w, h = det.bbox
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        label = f"{det.class_name} {det.confidence:.2f}"
        cv2.putText(frame, label, (x, y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Display result
    cv2.imshow('Object Detection', frame)
    
    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
cap.release()
cv2.destroyAllWindows()
```

### Batch Processing

```python
from pathlib import Path
from vision.object_detection import get_detector

# Initialize detector
detector = get_detector("yolo")

# Process all images in a directory
image_dir = Path("path/to/images")
output_dir = Path("path/to/output")
output_dir.mkdir(exist_ok=True)

for img_path in image_dir.glob("*.jpg"):
    # Detect objects
    detections = detector.detect(str(img_path))
    
    # Process detections...
    print(f"Processed {img_path.name}: {len(detections)} objects detected")
    
    # Save results
    with open(output_dir / f"{img_path.stem}.txt", "w") as f:
        for det in detections:
            f.write(f"{det.class_name} {det.confidence:.4f} {' '.join(map(str, det.bbox))}\n")
```

## Performance Tips

1. **Use GPU**: For best performance, use a CUDA-enabled GPU.
2. **Batch Processing**: When processing multiple images, consider batching them together.
3. **Image Size**: Smaller images process faster. Resize large images before detection if possible.
4. **Confidence Threshold**: Adjust the confidence threshold based on your needs to reduce false positives.

## Troubleshooting

### Model Loading Issues
- Ensure all required model files are in the correct locations.
- Check that the model format matches what the detector expects.

### Performance Problems
- Verify CUDA is properly installed if using GPU.
- Reduce input image size for faster processing.

### Detection Accuracy
- Adjust confidence threshold as needed.
- Consider training a custom model for specialized use cases.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
