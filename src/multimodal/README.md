# Multi-Modal Recognition System

This directory contains the implementation of a unified multi-modal recognition system that combines audio and visual data processing capabilities into a single, cohesive framework.

## Overview

The multi-modal recognition system provides an integrated approach to analyzing both audio and visual data, enabling applications to understand content across different modalities. This system bridges the gap between specialized audio and vision recognition components, creating a comprehensive recognition pipeline.

## Components

- **recognition_api.py**: The main integration point that provides a unified API for multi-modal recognition
- Supporting modules:
  - **audio**: Audio recognition components (speech, voice, music, sound)
  - **vision**: Visual recognition components (object detection, face recognition)

## Features

- Combined processing of audio and visual data
- Contextual understanding across modalities
- Support for various input formats (video, image+audio, live feed)
- Extensible architecture for adding new recognition capabilities

## Usage

```python
from src.multimodal.recognition_api import MultiModalRecognitionSystem

# Initialize the system
system = MultiModalRecognitionSystem()

# Process a video file (extracts and processes both audio and video)
results = system.process_video(
    video_path="path/to/video.mp4",
    extract_audio=True,
    frame_interval=10,
    confidence_threshold=0.5
)

# Process separate image and audio files
result = system.process_image_and_audio(
    image_path="path/to/image.jpg",
    audio_path="path/to/audio.wav",
    confidence_threshold=0.5
)

# Process live feed from camera and microphone
live_result = system.process_live_feed(
    camera_id=0,
    duration=5,
    confidence_threshold=0.5
)
```

## Advanced Usage Examples

See the [tutorial script](../../tutorials/multimodal_recognition_tutorial.py) for complete examples of how to use the multi-modal recognition system in different scenarios.

## Documentation

For detailed documentation on the multi-modal recognition system, refer to:
- [Unified Recognition Guide](../../docs/machine_learning/multimodal/unified_recognition_guide.md)

## References

- [Audio Recognition System](../audio/README.md)
- [Vision Recognition System](../vision/README.md)
- [Multi-Modal Recognition Tutorial](../../tutorials/multimodal_recognition_tutorial.py)
- [Multi-Modal Testing Suite](../../tests/test_multimodal_recognition.py)
