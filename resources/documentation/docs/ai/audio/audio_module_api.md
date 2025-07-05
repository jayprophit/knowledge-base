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
def __init__(self, :
            speech_model_path: Optional[str] = None,
            speech_scorer_path: Optional[str] = None,
            music_model_path: Optional[str] = None,
            sound_model_path: Optional[str] = None,
            sound_class_map_path: Optional[str] = None)
``````text
def process_audio(self, audio_file: str, extract_all: bool = False) -> Dict[str, Any]:
``````text
def identify_audio_type(self, audio_file: str) -> str
``````text
def recognize_from_microphone(self, duration: int = 5) -> Dict[str, Any]
``````text
def __init__(self, sample_rate: int = 16000, frame_length: int = 2048, hop_length: int = 512)
``````text
def extract_features(self, audio: np.ndarray, sr: Optional[int] = None) -> VoiceCharacteristics
``````text
def __init__(self, model_path: Optional[str] = None, sample_rate: int = SAMPLE_RATE)
``````text
def extract_features(self, audio: Union[str, np.ndarray], duration: Optional[float] = 30.0) -> MusicFeatures
``````text
def __init__(self, model_path: Optional[str] = None, sample_rate: int = 16000, n_fft: int = 2048, hop_length: int = 512)
``````text
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
``````text
### MusicFeatures
``````text
### SoundClassificationResult
```