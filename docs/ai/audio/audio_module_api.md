---
author: Knowledge Base Automation System
created_at: '2025-07-04'
description: Documentation on Audio Module Api for ai/audio
title: Audio Module Api
updated_at: '2025-07-04'
version: 1.0.0
---

# Audio Module API Reference

## Overview
The Audio Module provides comprehensive audio processing capabilities including speech recognition, voice analysis, music analysis, and sound classification. This document serves as the API reference for the main components.

## AudioRecognitionSystem

The main entry point for audio processing functionality.

### Constructor
```text
def __init__(self, 
            speech_model_path: Optional[str] = None,
            speech_scorer_path: Optional[str] = None,
            music_model_path: Optional[str] = None,
            sound_model_path: Optional[str] = None,
            sound_class_map_path: Optional[str] = None)
```text
- `speech_model_path`: Path to DeepSpeech model for speech recognition
- `speech_scorer_path`: Path to DeepSpeech scorer for speech recognition
- `music_model_path`: Path to music genre classification model
- `sound_model_path`: Path to sound classification model
- `sound_class_map_path`: Path to sound class mapping file

### Methods

#### process_audio
```text
def process_audio(self, audio_file: str, extract_all: bool = False) -> Dict[str, Any]
```text

**Parameters**:
- `audio_file`: Path to audio file
- `extract_all`: Whether to extract all features regardless of audio type

**Returns**:
Dictionary with recognition results

#### identify_audio_type
```text
def identify_audio_type(self, audio_file: str) -> str
```text

**Parameters**:
- `audio_file`: Path to audio file

**Returns**:
Audio type as string: 'speech', 'music', 'environmental', or 'unknown'

#### recognize_from_microphone
```text
def recognize_from_microphone(self, duration: int = 5) -> Dict[str, Any]
```text

**Parameters**:
- `duration`: Recording duration in seconds

**Returns**:
Dictionary with recognition results

## VoiceAnalyzer

Analyzes voice characteristics and performs speaker identification.

### Constructor
```text
def __init__(self, sample_rate: int = 16000, frame_length: int = 2048, hop_length: int = 512)
```text
- `sample_rate`: Sample rate for audio processing
- `frame_length`: Length of the analysis window in samples
- `hop_length`: Hop length between analysis windows

### Methods

#### extract_features
```text
def extract_features(self, audio: np.ndarray, sr: Optional[int] = None) -> VoiceCharacteristics
```
Extract voice characteristics from audio.

**Parameters**:
- `audio`: Audio samples
- `sr`: Sample rate (if None, use self.sample_rate)

**Returns**:
VoiceCharacteristics object with extracted features

## MusicAnalyzer

Analyzes music and extracts musical features.

### Constructor
```text
def __init__(self, model_path: Optional[str] = None, sample_rate: int = SAMPLE_RATE)
```text
- `model_path`: Path to pre-trained genre classification model
- `sample_rate`: Sample rate for audio processing

### Methods

#### extract_features
```text
def extract_features(self, audio: Union[str, np.ndarray], duration: Optional[float] = 30.0) -> MusicFeatures
```
Extract comprehensive music features from audio.

**Parameters**:
- `audio`: Audio file path or numpy array
- `duration`: Maximum duration to analyze (seconds)

**Returns**:
MusicFeatures object containing extracted features

## SoundClassifier

Classifies environmental sounds and audio events.

### Constructor
```text
def __init__(self, model_path: Optional[str] = None, sample_rate: int = 16000, n_fft: int = 2048, hop_length: int = 512)
```text
- `model_path`: Path to pre-trained sound classification model
- `sample_rate`: Sample rate for audio processing
- `n_fft`: FFT window size
- `hop_length`: Hop length between analysis windows

### Methods

#### classify_sound
```text
def cdef classify_sound(self, audio: Union[str, np.ndarray], 
                duration: Optional[float] = 5.0,
                top_k: int = 3) -> SoundClassificationResultClassify environmental sound.

**Parameters**:
- `audio`: Audio file path or numpy array
- `duration`: Maximum duration to analyze (seconds)
- `top_k`: Number of top predictions to return

**Returns**:
SoundClassificationResult object with classification results

## Data Classes

### VoiceCharacteristics
```python
@dataclass
class VoiceCharacteristics:
    pitch_hz: float
    pitch_std: float
    intensity_db: float
    speaking_rate: float
    hnr: float  # Harmonics-to-Noise Ratio
    mfcc: np.ndarray
    spectral_centroid: float
    spectral_bandwidth: float
    spectral_rolloff: float
    zero_crossing_rate: float
    formants: Optional[Dict[int, float]] = None
    gender: Optional[str] = None
    age_group: Optional[str] = None
    emotion: Optional[str] = None
```

### MusicFeatures
```python
@dataclass
class MusicFeatures:
    tempo: float
    beats: np.ndarray
    chroma: np.ndarray
    mfcc: np.ndarray
    spectral_contrast: np.ndarray
    tonnetz: np.ndarray
    key: str
    mode: str
    loudness: float
    zero_crossing_rate: float
    harmonic_percussive: Tuple[np.ndarray, np.ndarray]
    genre: Optional[str] = None
    genre_confidence: Optional[float] = None
    danceability: Optional[float] = None
    energy: Optional[float] = None
    valence: Optional[float] = None
    acousticness: Optional[float] = None
    instrumentalness: Optional[float] = None
    liveness: Optional[float] = None
    speechiness: Optional[float] = None
```

### SoundClassificationResult
```python
@datacl@dataclass
class SoundClassificationResult:
    label: str
    confidence: float
    category: Optional[str] = None  # E.g., "urban", "animal", "human", "nature"
    top_predictions: Optional[List[Dict[str, Any]]] = None
    source_file: Optional[str] = None
    duration: Optional[float] = None
    timestamp: Optional[float] = None  # For event detection in longer recordings"