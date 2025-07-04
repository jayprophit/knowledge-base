---
author: Knowledge Base Automation System
created_at: '2025-07-04'
description: Documentation on Audio Module Examples for ai/audio
title: Audio Module Examples
updated_at: '2025-07-04'
version: 1.0.0
---

# Audio Module Usage Examples

This document provides practical examples of how to use the audio module's components for various audio processing tasks.

## Table of Contents
- [Basic Setup](#basic-setup)
- [Speech Recognition](#speech-recognition)
- [Voice Analysis](#voice-analysis)
- [Music Analysis](#music-analysis)
- [Sound Classification](#sound-classification)
- [Complete Pipeline Example](#complete-pipeline-example)

## Basic Setup

First, install the required dependencies:

```bash
pip install numpy librosa soundfile pydub SpeechRecognition deepspeech
```

## Speech Recognition

### Basic Speech-to-Text

```python
from audio.recognition import AudioRecognitionSystem

# Initialize with default models
recognizer = AudioRecognitionSystem()

# Convert speech to text
text = recognizer.speech_to_text("speech_sample.wav")
print(f"Recognized text: {text}")
```

### Real-time Speech Recognition

```python
from audio.recognition import AudioRecognitionSystem

recognizer = AudioRecognitionSystem()

# Record and recognize from microphone
result = recognizer.recognize_from_microphone(duration=5)
print(f"Recognized: {result['text']}")
print(f"Confidence: {result['confidence']}")
```

## Voice Analysis

### Extract Voice Characteristics

```python
from audio.voice_analysis import VoiceAnalyzer
import librosa

# Initialize analyzer
analyzer = VoiceAnalyzer()

# Load audio
audio, sr = librosa.load("voice_sample.wav", sr=None)

# Analyze voice
features = analyzer.extract_features(audio, sr)

print(f"Pitch: {features.pitch_hz:.1f} Hz")
print(f"Speaking rate: {features.speaking_rate:.1f} words/sec")
print(f"Estimated gender: {features.gender}")
print(f"Estimated emotion: {features.emotion}")
```

### Speaker Identification

```python
from audio.voice_analysis import VoiceAnalyzer

analyzer = VoiceAnalyzer()

# Enroll known speakers
analyzer.enroll_speaker("alice", "alice_voice_sample.wav")
analyzer.enroll_speaker("bob", "bob_voice_sample.wav")

# Identify unknown speaker
result = analyzer.identify_speaker("unknown_voice.wav")
print(f"Identified as: {result['speaker']} (confidence: {result['confidence']:.2f})")
```

## Music Analysis

### Extract Music Features

```python
from audio.music_analysis import MusicAnalyzer

analyzer = MusicAnalyzer()

# Analyze music file
features = analyzer.extract_features("song.mp3")

print(f"Tempo: {features.tempo:.1f} BPM")
print(f"Key: {features.key} {features.mode}")
print(f"Genre: {features.genre} (confidence: {features.genre_confidence*100:.1f}%)")
print(f"Danceability: {features.danceability:.2f}")
print(f"Energy: {features.energy:.2f}")
```

### Music Genre Classification

```python
from audio.music_analysis import MusicAnalyzer

# Initialize with custom model
analyzer = MusicAnalyzer(model_path="custom_genre_model.h5")

# Classify genre
result = analyzer.classify_genre("unknown_song.wav", top_k=3)

print("Top genre predictions:")
for i, (genre, conf) in enumerate(zip(result.genres, result.confidences), 1):
    print(f"{i}. {genre}: {conf*100:.1f}%")
```

## Sound Classification

### Environmental Sound Classification

```python
from audio.sound_classification import SoundClassifier

classifier = SoundClassifier()

# Classify sound
result = classifier.classify_sound("environmental_sound.wav")

print(f"Detected sound: {result.label}")
print(f"Confidence: {result.confidence:.2f}")
print(f"Category: {result.category}")
```

### Event Detection in Audio

```python
from audio.sound_classification import SoundClassifier

classifier = SoundClassifier()

# Detect events in a long recording
events = classifier.detect_events("long_recording.wav", 
                                threshold=0.7, 
                                min_duration=1.0,
                                max_gap=0.5)

print("Detected events:")
for event in events:
    print(f"- {event['label']} at {event['start_time']:.1f}s (duration: {event['duration']:.1f}s)")"'"'
```

## Complete Pipeline Example

Here's how to use the complete audio processing pipeline:

```python
from audio.recognition import AudioRecognitionSystem

# Initialize with all models
recognizer = AudioRecognitionSystem(
    speech_model_path="deepspeech-0.9.3-models.pbmm",
    speech_scorer_path="deepspeech-0.9.3-models.scorer",
    music_model_path="music_genre_model.h5",
    sound_model_path="sound_classifier.h5"
)

# Process audio file
result = recognizer.process_audio("mixed_audio.wav", extract_all=True)

# Print results
print(f"Audio type: {result['audio_type']}")

if result['audio_type'] == 'speech':
    print(f"Transcription: {result['speech']['text']}")
    print(f"Speaker: {result['voice']['speaker']} ({result['voice']['gender']})")
    print(f"Emotion: {result['voice']['emotion']}")
    
elif result['audio_type'] == 'music':
    print(f"Genre: {result['music']['genre']}")
    print(f"Tempo: {result['music']['tempo']} BPM")
    print(f"Key: {result['music']['key']} {result['music']['mode']}")
    
elif result['audio_type'] == 'environmental':
    print(f"Detected sound: {result['sound']['label']}")
    print(f"Category: {result['sound']['category']}")
    
# Save results to JSON
import json
with open('audio_analysis.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)
```

## Advanced Usage

### Custom Model Integration

```python
from audio.recognition import AudioRecognitionSystem
from tensorflow.keras.models import load_model

# Load custom models
custom_music_model = load_model('custom_music_model.h5')
custom_sound_model = load_model('custom_sound_model.h5')

# Initialize with custom models
recognizer = AudioRecognitionSystem(
    music_model=custom_music_model,
    sound_model=custom_sound_model
)
```

### Batch Processing

```python
from audio.recognition import AudioRecognitionSystem
from pathlib import Path

recognizer = AudioRecognitionSystem()

# Process all audio files in a directory
audio_dir = Path("audio_samples")
for audio_file in audio_dir.glob("*.wav"):
    print(f"\nProcessing {audio_file.name}")
    result = recognizer.process_audio(str(audio_file))
    print(f"Type: {result['audio_type']}")
    
    if 'speech' in result:
        print(f"Text: {result['speech']['text']}")
    
    if 'music' in result:
        print(f"Genre: {result['music']['genre']}")
    
    if 'sound' in result:
        print(f"Sound: {result['sound']['label']}")
```

### Real-time Audio Processing

```python
import pyaudio
import numpy as np
from audio.recognition import AudioRecognitionSystem

# Initialize recognizer
recognizer = AudioRecognitionSystem()

# Audio parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("Listening... (press Ctrl+C to stop)")

try:
    while True:
        # Read audio data
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio = np.frombuffer(data, dtype=np.int16)
        
        # Process audio in real-time
        result = recognizer.process_audio_chunk(audio, RATE)
        
        if result['speech_detected']:
            print(f"\nDetected speech: {result['text']}")
            
except KeyboardInterrupt:
    print("\nStopping...")
    
finally:
    # Clean up
    stream.stop_stream()
    stream.close()
    p.terminate()
```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   # Install all required dependencies
   pip install -r requirements.txt
   ```

2. **Model Files Not Found**
   - Download required model files (DeepSpeech, etc.)
   - Update paths in your code or configuration

3. **Audio Format Issues**
   - Ensure audio is in a supported format (WAV, MP3, etc.)
   - Check sample rate (16kHz is commonly used for speech)
   - Convert stereo to mono if needed

### Performance Tips

1. **Batch Processing**
   - Process multiple files in batches for better performance
   - Use `multiprocessing` for CPU-bound tasks

2. **Model Optimization**
   - Use quantized models for faster inference
   - Enable GPU acceleration if available
   - Reduce input size or model complexity if needed

3. **Memory Management**
   - Process large files in chunks
   - Clear unused variables and models
   - Use generators for large datasets

## Additional Resources

- [Librosa Documentation](https://librosa.org/doc/latest/index.html)
- [DeepSpeech Documentation](https://deepspeech.readthedocs.io/)
- [TensorFlow Audio Tutorials](https://www.tensorflow.org/tutorials/audio/simple_audio)
- [PyAudio Documentation](https://people.csail.mit.edu/hubert/pyaudio/docs/)

---
*Last Updated: 2025-06-30*
