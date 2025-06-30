# Unified Multi-Modal Recognition System

This guide provides documentation for the unified multi-modal recognition system that integrates audio and visual recognition capabilities into a seamless framework.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Key Components](#key-components)
5. [Usage Examples](#usage-examples)
6. [Performance Optimization](#performance-optimization)
7. [Extension and Customization](#extension-and-customization)
8. [Troubleshooting](#troubleshooting)

## Overview

The unified multi-modal recognition system combines our audio and visual recognition components into a cohesive framework that can process and analyze different types of media. This allows for sophisticated applications like:

- Video content analysis with synchronized audio and visual processing
- Combined image and audio processing for context-rich understanding
- Real-time multi-modal analysis from camera and microphone feeds
- Contextual scene understanding across modalities

The system is designed to be modular, extensible, and easy to integrate with existing applications. It provides a high-level API that abstracts the complexity of individual recognition systems while maintaining their full capabilities.

## Architecture

The unified multi-modal recognition system follows a layered architecture:

```
┌───────────────────────────────────────────────────────────────┐
│                MultiModalRecognitionSystem                    │
└───────────────────────────┬───────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
┌───────────▼───────────┐   ┌───────────────▼─────────┐
│  AudioRecognitionSystem│   │  Vision Recognition     │
└─────────┬─────────────┘   └───────────┬─────────────┘
          │                             │
┌─────────┼─────────────┐   ┌───────────┼─────────────┐
│         │             │   │           │             │
▼         ▼             ▼   ▼           ▼             ▼
┌─────┐ ┌─────┐     ┌─────┐ ┌─────┐   ┌─────┐     ┌─────┐
│Speech│ │Voice│     │Sound│ │YOLO │   │Face │     │Scene│
│Recog.│ │Analys│    │Class│ │Detect│  │Detect│    │Class│
└─────┘ └─────┘     └─────┘ └─────┘   └─────┘     └─────┘
```

The system integrates the following components:

1. **Audio Recognition**: Handles speech recognition, voice analysis, music analysis, and sound classification
2. **Vision Recognition**: Manages object detection, face detection, and scene classification
3. **Multi-Modal Integration**: Combines results from different modalities and generates contextual understanding

## Installation

### Prerequisites

- Python 3.8+
- TensorFlow 2.5+
- PyTorch 1.9+
- OpenCV 4.5+
- Librosa 0.9+
- FFmpeg (for video processing)

### Setup

1. Install the required packages:

```bash
pip install tensorflow torch torchvision opencv-python librosa SpeechRecognition
```

2. Install additional dependencies:

```bash
pip install pydub parselmouth scikit-learn
```

3. Ensure FFmpeg is installed for video processing:

```bash
# Ubuntu/Debian
apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

## Key Components

### MultiModalRecognitionSystem

The main entry point for unified recognition tasks. It provides methods for:

- `process_video()`: Process video files with both audio and visual analysis
- `process_image_and_audio()`: Process separate image and audio files
- `process_live_feed()`: Process real-time camera and microphone input

### MultiModalResult

A data class that stores the results of multi-modal recognition, including:

- Audio analysis results (speech, voice, music, sounds)
- Visual analysis results (objects, faces, scenes)
- Combined contextual understanding
- Source metadata and timestamps

## Usage Examples

### Process a Video File

```python
from src.multimodal.recognition_api import MultiModalRecognitionSystem

# Initialize the system
system = MultiModalRecognitionSystem(
    vision_model_type="yolo"  # Options: "yolo", "face"
)

# Process a video file
results = system.process_video(
    video_path="path/to/video.mp4",
    extract_audio=True,
    frame_interval=10,  # Process every 10th frame
    confidence_threshold=0.5
)

# Access combined results
print(f"Analyzed {results['video_analysis']['frames_analyzed']} frames")
print(f"Detected {len(results['video_analysis']['objects_detected'])} unique objects")

# Access audio analysis results
if results['audio_analysis']:
    if results['audio_analysis'].get('speech_recognition'):
        print(f"Transcript: {results['audio_analysis']['speech_recognition']['text']}")
        
    if results['audio_analysis'].get('sound_classification'):
        print(f"Sound: {results['audio_analysis']['sound_classification']['label']}")

# Access contextual understanding
if results.get('context'):
    print("Scene description:", ", ".join(results['context']['scene_description']))
    print("Audio context:", ", ".join(results['context']['audio_context']))
```

### Process Image and Audio Together

```python
# Process separate image and audio files with combined analysis
result = system.process_image_and_audio(
    image_path="path/to/image.jpg",
    audio_path="path/to/audio.wav",
    confidence_threshold=0.6
)

# Access results
if result.objects_detected:
    print("Objects detected:")
    for obj in result.objects_detected:
        print(f"- {obj['class_name']} ({obj['confidence']:.2f})")

if result.speech_recognition:
    print(f"Speech: {result.speech_recognition['text']}")

# Access combined context
if result.context:
    print("Combined context:")
    print("Scene:", ", ".join(result.context['scene_description']))
    print("Audio:", ", ".join(result.context['audio_context']))
```

### Real-time Camera and Microphone Processing

```python
# Process live feed from camera and microphone
live_result = system.process_live_feed(
    camera_id=0,  # Default camera
    duration=5,   # Record 5 seconds of audio
    confidence_threshold=0.5
)

# Access real-time recognition results
if live_result.speech_recognition:
    print(f"You said: {live_result.speech_recognition['text']}")

if live_result.objects_detected:
    print("Objects in view:")
    for obj in live_result.objects_detected:
        print(f"- {obj['class_name']}")
```

## Performance Optimization

For optimal performance when using the multi-modal recognition system:

1. **Adjust Frame Interval**: Process fewer frames for faster video analysis
   ```python
   results = system.process_video(video_path, frame_interval=30)  # Process every 30th frame
   ```

2. **Use Confidence Thresholds**: Filter low-confidence detections
   ```python
   results = system.process_video(video_path, confidence_threshold=0.7)  # Only keep confident detections
   ```

3. **GPU Acceleration**: Ensure TensorFlow and PyTorch are using GPU when available
   ```python
   system = MultiModalRecognitionSystem(device="cuda")  # Force GPU usage
   ```

4. **Limit Audio Duration**: For long videos, limit audio processing duration
   ```python
   # Extract only first 60 seconds of audio
   import os
   os.system(f'ffmpeg -i "{video_path}" -t 60 -q:a 0 -map a "{audio_path}" -y')
   ```

## Extension and Customization

The multi-modal recognition system is designed to be extensible. Here's how to customize it:

### Add Custom Vision Models

```python
from src.vision.custom_detector import CustomDetector
from src.multimodal.recognition_api import MultiModalRecognitionSystem

# Create custom detector
custom_detector = CustomDetector(model_path="path/to/custom_model.pt")

# Initialize system with custom detector
system = MultiModalRecognitionSystem()
system.vision_system = custom_detector
```

### Add Custom Audio Processors

```python
from src.audio.custom_processor import CustomAudioProcessor
from src.multimodal.recognition_api import MultiModalRecognitionSystem

# Create custom audio processor
custom_processor = CustomAudioProcessor(model_path="path/to/custom_model.h5")

# Initialize system
system = MultiModalRecognitionSystem()

# Add custom processor to audio system
system.audio_system.custom_processor = custom_processor

# Extend process_audio method to use custom processor
original_process_audio = system.audio_system.process_audio

def extended_process_audio(audio_file):
    results = original_process_audio(audio_file)
    results['custom_analysis'] = system.audio_system.custom_processor.analyze(audio_file)
    return results

system.audio_system.process_audio = extended_process_audio
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**
   - Ensure all dependencies are installed
   - Check Python path includes the project root directory

2. **CUDA Out of Memory**
   - Reduce batch size or frame processing rate
   - Use smaller models for edge devices

3. **Video Processing Errors**
   - Verify FFmpeg is installed and accessible
   - Check video file is not corrupted

4. **Audio Extraction Issues**
   - Ensure video contains an audio track
   - Check FFmpeg installation

### Logging and Debugging

Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize system with verbose logging
system = MultiModalRecognitionSystem()
```

## Resources

- **Audio Recognition Documentation**: [Audio Recognition Guide](../audio_recognition/audio_recognition_guide.md)
- **Vision Recognition Documentation**: [Vision Recognition Guide](../vision_recognition/vision_recognition_guide.md)
- **Model Downloads**: [Pre-trained Models](https://example.com/models)
- **Training Scripts**: [Custom Model Training](../training/training_guide.md)
