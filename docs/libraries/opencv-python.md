# opencv-python Library

## Overview
[opencv-python](https://pypi.org/project/opencv-python/) is a Python wrapper for OpenCV, a powerful computer vision library. It provides image and video processing, object detection, and facial recognition capabilities.

## Installation
```sh
pip install opencv-python
```

## Example Usage
```python
import cv2
image = cv2.imread('path/to/image.jpg')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
cv2.imshow('Gray Image', gray)
cv2.waitKey(0)
cv2.destroyAllWindows()
```

## Integration Notes
- Used for vision, object detection, and camera input in the assistant.
- Integrates with face_recognition, dlib, and other ML libraries.

## Cross-links
- [virtual_assistant_book.md](../virtual_assistant_book.md)
- [ai_agents.md](../ai_agents.md)
- [Vision Module](../../src/vision/README.md)

---
_Last updated: July 3, 2025_
