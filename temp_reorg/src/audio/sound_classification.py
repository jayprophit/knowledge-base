"""
Sound Classification Module

This module provides functionality for environmental sound classification including
urban sounds, animal sounds, and general audio event detection.
"""

import os
import numpy as np
import librosa
import tensorflow as tf
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union, Any
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SoundClassificationResult:
    """Data class to store sound classification results."""
    label: str
    confidence: float
    category: Optional[str] = None  # E.g., "urban", "animal", "human", "nature"
    top_predictions: Optional[List[Dict[str, Any]]] = None
    source_file: Optional[str] = None
    duration: Optional[float] = None
    timestamp: Optional[float] = None  # For event detection in longer recordings


class SoundClassifier:
    """Class for classifying environmental sounds and audio events."""
    
    # Common sound categories
    URBAN_SOUNDS = [
        'car_horn', 'siren', 'street_music', 'drilling', 'engine_idling',
        'jackhammer', 'air_conditioner', 'children_playing'
    ]
    
    ANIMAL_SOUNDS = [
        'dog_bark', 'bird_chirp', 'cat_meow', 'frog_croak', 'insect_buzz',
        'rooster', 'pig_oink', 'cow_moo', 'hen', 'sheep_bleat'
    ]
    
    HUMAN_SOUNDS = [
        'cough', 'footstep', 'laughter', 'crying', 'sneezing',
        'clapping', 'breathing', 'snoring', 'drinking', 'typing'
    ]
    
    NATURE_SOUNDS = [
        'rain', 'thunderstorm', 'wind', 'water_stream', 'sea_waves',
        'fire_crackling', 'forest', 'leaves_rustling'
    ]
    
    def __init__(self, model_path: Optional[str] = None, sample_rate: int = 22050):
        """Initialize the sound classifier.
        
        Args:
            model_path: Path to a pre-trained sound classification model
            sample_rate: Sample rate for audio processing
        """
        self.sample_rate = sample_rate
        self.model = None
        self.class_names = []
        self.hop_length = 512
        self.n_fft = 2048
        
        # Load classification model if provided
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def load_model(self, model_path: str, class_map_path: Optional[str] = None):
        """Load a pre-trained sound classification model.
        
        Args:
            model_path: Path to the model file (HDF5 or SavedModel)
            class_map_path: Optional path to JSON file mapping indices to class names
        """
        try:
            self.model = tf.keras.models.load_model(model_path)
            logger.info(f"Loaded sound classification model from {model_path}")
            
            # Load class names if provided
            if class_map_path and os.path.exists(class_map_path):
                import json
                with open(class_map_path, 'r') as f:
                    self.class_names = json.load(f)
                logger.info(f"Loaded {len(self.class_names)} class names")
            else:
                # Default to UrbanSound8K classes if no class map is provided
                self.class_names = [
                    'air_conditioner', 'car_horn', 'children_playing',
                    'dog_bark', 'drilling', 'engine_idling', 'gun_shot',
                    'jackhammer', 'siren', 'street_music'
                ]
                
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def load_audio(self, audio_path: Union[str, np.ndarray], 
                  duration: Optional[float] = None) -> np.ndarray:
        """Load audio file or use provided numpy array.
        
        Args:
            audio_path: Path to audio file or numpy array of audio samples
            duration: Maximum duration in seconds (None for full duration)
            
        Returns:
            Audio signal as numpy array
        """
        if isinstance(audio_path, (str, Path)):
            y, sr = librosa.load(audio_path, sr=self.sample_rate, duration=duration, mono=True)
        elif isinstance(audio_path, np.ndarray):
            y = audio_path
            if len(y.shape) > 1:
                y = librosa.to_mono(y)
            if duration and len(y) > duration * self.sample_rate:
                y = y[:int(duration * self.sample_rate)]
        else:
            raise ValueError("audio_path must be a file path or numpy array")
            
        return y
    
    def extract_features(self, audio: np.ndarray) -> np.ndarray:
        """Extract audio features for sound classification.
        
        Args:
            audio: Audio samples as numpy array
            
        Returns:
            Feature matrix suitable for model input
        """
        # Extract MFCC features
        mfccs = librosa.feature.mfcc(
            y=audio, 
            sr=self.sample_rate, 
            n_mfcc=40,
            hop_length=self.hop_length,
            n_fft=self.n_fft
        )
        
        # Calculate statistics for each coefficient
        mfcc_mean = np.mean(mfccs, axis=1)
        mfcc_std = np.std(mfccs, axis=1)
        mfcc_max = np.max(mfccs, axis=1)
        mfcc_min = np.min(mfccs, axis=1)
        
        # Extract spectral features
        spectral_centroid = librosa.feature.spectral_centroid(
            y=audio, 
            sr=self.sample_rate, 
            hop_length=self.hop_length,
            n_fft=self.n_fft
        )
        spectral_bandwidth = librosa.feature.spectral_bandwidth(
            y=audio, 
            sr=self.sample_rate, 
            hop_length=self.hop_length,
            n_fft=self.n_fft
        )
        spectral_rolloff = librosa.feature.spectral_rolloff(
            y=audio, 
            sr=self.sample_rate, 
            hop_length=self.hop_length,
            n_fft=self.n_fft
        )
        zero_crossing_rate = librosa.feature.zero_crossing_rate(
            audio,
            hop_length=self.hop_length
        )
        
        # Calculate statistics for spectral features
        centroid_mean = np.mean(spectral_centroid)
        bandwidth_mean = np.mean(spectral_bandwidth)
        rolloff_mean = np.mean(spectral_rolloff)
        zcr_mean = np.mean(zero_crossing_rate)
        
        # Extract temporal features
        rms = librosa.feature.rms(y=audio, hop_length=self.hop_length)
        rms_mean = np.mean(rms)
        
        # Combine all features
        feature_vector = np.concatenate([
            mfcc_mean, mfcc_std, mfcc_max, mfcc_min,
            [centroid_mean, bandwidth_mean, rolloff_mean, zcr_mean, rms_mean]
        ])
        
        return feature_vector
    
    def classify_sound(self, audio: Union[str, np.ndarray], 
                      duration: Optional[float] = 5.0,
                      top_k: int = 3) -> SoundClassificationResult:
        """Classify environmental sound.
        
        Args:
            audio: Audio file path or numpy array
            duration: Maximum duration to analyze (seconds)
            top_k: Number of top predictions to return
            
        Returns:
            SoundClassificationResult object with classification results
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Load audio
        y = self.load_audio(audio, duration=duration)
        
        # Extract features
        features = self.extract_features(y)
        
        # Reshape for model input (add batch dimension)
        features = np.expand_dims(features, axis=0)
        
        # Make prediction
        try:
            predictions = self.model.predict(features)[0]
            
            # Get top K predictions
            top_indices = np.argsort(predictions)[-top_k:][::-1]
            top_values = predictions[top_indices]
            
            # Get class names
            top_classes = [
                self.class_names[i] if i < len(self.class_names) else f"class_{i}"
                for i in top_indices
            ]
            
            # Prepare top predictions
            top_predictions = [
                {"label": cls, "confidence": float(conf)}
                for cls, conf in zip(top_classes, top_values)
            ]
            
            # Get category
            category = self._get_sound_category(top_classes[0])
            
            # Create result
            source_file = audio if isinstance(audio, str) else None
            result = SoundClassificationResult(
                label=top_classes[0],
                confidence=float(top_values[0]),
                category=category,
                top_predictions=top_predictions,
                source_file=source_file,
                duration=duration
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return SoundClassificationResult(
                label="unknown",
                confidence=0.0,
                top_predictions=[{"label": "error", "confidence": 0.0}]
            )
    
    def _get_sound_category(self, sound_label: str) -> str:
        """Determine the category of a sound based on its label.
        
        Args:
            sound_label: The sound label to categorize
            
        Returns:
            Category name (urban, animal, human, nature, or unknown)
        """
        sound_label = sound_label.lower()
        
        if any(label in sound_label for label in self.URBAN_SOUNDS):
            return "urban"
        elif any(label in sound_label for label in self.ANIMAL_SOUNDS):
            return "animal"
        elif any(label in sound_label for label in self.HUMAN_SOUNDS):
            return "human"
        elif any(label in sound_label for label in self.NATURE_SOUNDS):
            return "nature"
        else:
            return "unknown"
    
    def detect_sound_events(self, audio: Union[str, np.ndarray], 
                           window_size: float = 1.0,
                           hop_size: float = 0.5,
                           threshold: float = 0.5) -> List[SoundClassificationResult]:
        """Detect sound events in a longer audio recording.
        
        Args:
            audio: Audio file path or numpy array
            window_size: Size of analysis window in seconds
            hop_size: Hop size between windows in seconds
            threshold: Confidence threshold for detection
            
        Returns:
            List of SoundClassificationResult objects for detected events
        """
        # Load full audio
        y = self.load_audio(audio)
        
        # Calculate window and hop sizes in samples
        window_samples = int(window_size * self.sample_rate)
        hop_samples = int(hop_size * self.sample_rate)
        
        # Initialize results list
        results = []
        
        # Process audio in sliding windows
        for i in range(0, len(y) - window_samples, hop_samples):
            # Extract window
            window = y[i:i+window_samples]
            
            # Classify window
            result = self.classify_sound(window)
            
            # Add timestamp
            result.timestamp = i / self.sample_rate
            
            # Add to results if confidence exceeds threshold
            if result.confidence >= threshold:
                results.append(result)
        
        return results


# Example usage
if __name__ == "__main__":
    # Initialize sound classifier
    classifier = SoundClassifier()
    
    try:
        # Example: Load a pre-trained model
        # classifier.load_model("path/to/sound_model.h5")
        
        # Classify a sound file
        # result = classifier.classify_sound("path/to/sound.wav")
        # print(f"Detected sound: {result.label} (confidence: {result.confidence:.2f})")
        # print(f"Category: {result.category}")
        
        # Example: Detect sound events in a longer recording
        # events = classifier.detect_sound_events("path/to/recording.wav")
        # for i, event in enumerate(events):
        #     print(f"Event {i+1}: {event.label} at {event.timestamp:.2f}s (confidence: {event.confidence:.2f})")
        
        print("Sound classification module loaded successfully")
    
    except Exception as e:
        print(f"Error: {e}")
