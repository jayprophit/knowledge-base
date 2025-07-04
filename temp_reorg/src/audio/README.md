# Audio Processing Module

This module provides comprehensive audio processing capabilities including speech recognition, voice analysis, music analysis, and sound classification. It's designed to be modular, extensible, and easy to use for a variety of audio processing tasks.

## Features

- **Speech Recognition**: Convert speech to text using multiple backends (Google Web Speech, DeepSpeech)
- **Voice Analysis**: Extract voice characteristics, speaker identification, voice activity detection
- **Music Analysis**: Genre classification, beat tracking, key detection, structural segmentation
- **Sound Classification**: Classify environmental sounds, music, speech, and more
- **Multi-format Support**: Works with various audio file formats and real-time microphone input

## Installation

1. Install the required dependencies:

```bash
# Core dependencies
pip install librosa numpy soundfile tensorflow

# For speech recognition
pip install SpeechRecognition pydub

# For DeepSpeech (optional)
pip install deepspeech

# For voice analysis (optional)
pip install parselmouth

# For music analysis
pip install scikit-learn
```

## Usage

### Speech Recognition

```python
from audio import SpeechRecognizer

# Initialize with DeepSpeech model (optional)
recognizer = SpeechRecognizer(
    model_path="deepspeech-0.9.3-models.pbmm",
    scorer_path="deepspeech-0.9.3-models.scorer"
)

# Recognize from microphone
result = recognizer.recognize_from_microphone(duration=5)
print(f"You said: {result.text}")

# Recognize from audio file
result = recognizer.recognize_google("path/to/audio.wav")
print(f"Transcription: {result.text}")

# Use DeepSpeech for offline recognition (if model is loaded)
if recognizer.ds_model:
    result = recognizer.recognize_deepspeech("path/to/audio.wav")
    print(f"Offline transcription: {result.text}")
```

### Voice Analysis

```python
from audio import VoiceAnalyzer

# Initialize voice analyzer
analyzer = VoiceAnalyzer()

# Create speaker profile
profile = analyzer.create_speaker_profile("path/to/speaker1.wav", "speaker1")
print(f"Created profile for {profile['speaker_id']}")

# Identify speaker from unknown audio
results = analyzer.identify_speaker("path/to/unknown.wav", top_n=3)
for i, result in enumerate(results, 1):
    print(f"{i}. {result['speaker_id']} (confidence: {result['similarity']:.2f})")

# Extract voice characteristics
audio, sr = analyzer.load_audio("path/to/audio.wav")
features = analyzer.extract_features(audio, sr)
print(f"Pitch: {features.pitch_hz:.1f} Hz")
print(f"Gender: {features.gender}")
print(f"Speaking rate: {features.speaking_rate:.1f} syllables/sec")
```

### Music Analysis

```python
from audio import MusicAnalyzer

# Initialize music analyzer
analyzer = MusicAnalyzer()

# Extract music features
features = analyzer.extract_features("path/to/song.mp3")
print(f"Tempo: {features.tempo:.1f} BPM")
print(f"Key: {features.key} {features.mode}")
print(f"Danceability: {features.danceability:.2f}")
print(f"Energy: {features.energy:.2f}")

# Get beat times
beat_times = analyzer.get_beat_times("path/to/song.mp3")
print(f"First 5 beats at: {beat_times[:5]} seconds")

# Segment song into sections
segments = analyzer.get_segments("path/to/song.mp3", method='mfcc')
for i, segment in enumerate(segments, 1):
    print(f"Segment {i}: {segment['start']:.1f}s - {segment['end']:.1f}s ({segment['label']})")
```

## Modules

### 1. Speech Recognition (`speech_recognition.py`)

- Supports multiple recognition backends (Google Web Speech, DeepSpeech)
- Real-time microphone input
- Audio file processing
- Confidence scoring and alternatives

### 2. Voice Analysis (`voice_analysis.py`)

- Speaker identification
- Voice characteristics extraction (pitch, intensity, HNR, etc.)
- Voice activity detection
- Speaker profile management

### 3. Music Analysis (`music_analysis.py`)

- Tempo and beat tracking
- Key and mode detection
- Genre classification
- Music feature extraction (MFCC, chroma, spectral features)
- Structural segmentation
- Audio feature estimation (danceability, energy, valence, etc.)

### 4. Sound Classification (`sound_classification.py`)

- Environmental sound classification
- Music/speech/noise discrimination
- Custom model support

## Performance Considerations

- **Real-time Processing**: For real-time applications, consider using smaller models or feature extraction windows
- **Memory Usage**: Processing long audio files may require significant memory. Process in chunks if needed.
- **GPU Acceleration**: TensorFlow operations will automatically use GPU if available
- **Sampling Rate**: Different modules may have optimal sampling rates (e.g., 16kHz for speech, 22.05kHz for music)

## Extending the Module

1. **Add New Models**: Subclass the base classes to implement custom models
2. **Add Features**: Extend the feature extractors with additional audio features
3. **Custom Pipelines**: Create custom processing pipelines by combining different modules

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Librosa for audio feature extraction
- TensorFlow for deep learning support
- Mozilla DeepSpeech for offline speech recognition
- Google Web Speech API for cloud-based recognition
