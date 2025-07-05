"""
Music Analysis Module

This module provides functionality for music analysis including genre classification,
beat tracking, key detection, and music feature extraction.
"""

import os
import numpy as np
import librosa
import tensorflow as tf
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MusicFeatures:
    """Data class to store music analysis features."""
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

class MusicAnalyzer:
    """Class for analyzing music and extracting musical features."""
    
    # Standard sample rate for music analysis
    SAMPLE_RATE = 22050
    
    # Standard hop length for analysis
    HOP_LENGTH = 512
    
    # Standard frame length for analysis
    N_FFT = 2048
    
    # Standard genre classes (GTZAN dataset)
    GENRES = [
        'blues', 'classical', 'country', 'disco', 'hiphop', 
        'jazz', 'metal', 'pop', 'reggae', 'rock'
    ]
    
    def __init__(self, model_path: Optional[str] = None, sample_rate: int = SAMPLE_RATE):
        """Initialize the music analyzer.
        
        Args:
            model_path: Path to a pre-trained genre classification model
            sample_rate: Sample rate for audio processing
        """
        self.sample_rate = sample_rate
        self.model = None
        
        # Load genre classification model if provided
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """Load a pre-trained music genre classification model.
        
        Args:
            model_path: Path to the model file (HDF5 or SavedModel)
        """
        try:
            self.model = tf.keras.models.load_model(model_path)
            logger.info(f"Loaded music analysis model from {model_path}")
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
            Mono audio signal as a numpy array
        """
        if isinstance(audio_path, (str, Path)):
            y, _ = librosa.load(audio_path, sr=self.sample_rate, duration=duration, mono=True)
        elif isinstance(audio_path, np.ndarray):
            y = audio_path
            if len(y.shape) > 1:
                y = librosa.to_mono(y)
            if duration and len(y) > duration * self.sample_rate:
                y = y[:int(duration * self.sample_rate)]
        else:
            raise ValueError("audio_path must be a file path or numpy array")
            
        return y
    
    def extract_features(self, audio: Union[str, np.ndarray], 
                        duration: Optional[float] = 30.0) -> MusicFeatures:
        """Extract comprehensive music features from audio.
        
        Args:
            audio: Audio file path or numpy array
            duration: Maximum duration to analyze (seconds)
            
        Returns:
            MusicFeatures object containing extracted features
        """
        # Load audio
        y = self.load_audio(audio, duration)
        
        # Extract tempo and beats
        tempo, beats = librosa.beat.beat_track(
            y=y, 
            sr=self.sample_rate, 
            hop_length=self.HOP_LENGTH
        )
        
        # Extract chroma features
        chroma = librosa.feature.chroma_stft(
            y=y, 
            sr=self.sample_rate, 
            hop_length=self.HOP_LENGTH
        )
        
        # Extract MFCCs
        mfcc = librosa.feature.mfcc(
            y=y, 
            sr=self.sample_rate, 
            n_mfcc=20,
            hop_length=self.HOP_LENGTH,
            n_fft=self.N_FFT
        )
        
        # Extract spectral contrast
        spectral_contrast = librosa.feature.spectral_contrast(
            y=y, 
            sr=self.sample_rate,
            hop_length=self.HOP_LENGTH
        )
        
        # Extract tonnetz features
        tonnetz = librosa.feature.tonnetz(
            y=librosa.effects.harmonic(y),
            sr=self.sample_rate
        )
        
        # Estimate key and mode
        key, mode = self._estimate_key(y)
        
        # Calculate loudness (RMS energy in dB)
        rms_energy = librosa.feature.rms(
            y=y, 
            frame_length=self.N_FFT, 
            hop_length=self.HOP_LENGTH
        )
        loudness = 20 * np.log10(np.mean(rms_energy) + 1e-10)
        
        # Separate harmonic and percussive components
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        
        # Calculate zero-crossing rate
        zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(
            y=y, 
            frame_length=self.N_FFT, 
            hop_length=self.HOP_LENGTH
        ))
        
        # Create MusicFeatures object
        features = MusicFeatures(
            tempo=float(tempo),
            beats=beats,
            chroma=chroma,
            mfcc=mfcc,
            spectral_contrast=spectral_contrast,
            tonnetz=tonnetz,
            key=key,
            mode=mode,
            loudness=float(loudness),
            zero_crossing_rate=float(zero_crossing_rate),
            harmonic_percussive=(y_harmonic, y_percussive)
        )
        
        # If model is available, predict genre
        if self.model is not None:
            genre, confidence = self.predict_genre(y)
            features.genre = genre
            features.genre_confidence = confidence
            
            # Estimate additional audio features
            features = self._estimate_audio_features(features, y)
        
        return features
    
    def _estimate_key(self, y: np.ndarray) -> Tuple[str, str]:
        """Estimate the musical key and mode."""
        # Get chroma features
        chroma = librosa.feature.chroma_cqt(y=y, sr=self.sample_rate)
        
        # Get the most common pitch class
        key_pitch = np.argmax(np.sum(chroma, axis=1))
        
        # Major and minor keys
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Simple heuristic for major/minor
        # Compare energy in major and minor triads
        major_triad = [0, 4, 7]  # Major third (4 semitones), perfect fifth (7 semitones)
        minor_triad = [0, 3, 7]   # Minor third (3 semitones), perfect fifth (7 semitones)
        
        major_energy = 0
        minor_energy = 0
        
        for i in range(len(keys)):
            major_energy += np.sum(chroma[(key_pitch + np.array(major_triad)) % 12])
            minor_energy += np.sum(chroma[(key_pitch + np.array(minor_triad)) % 12])
        
        mode = 'major' if major_energy > minor_energy else 'minor'
        key = keys[key_pitch]
        
        return key, mode
    
    def _estimate_audio_features(self, features: MusicFeatures, 
                               y: np.ndarray) -> MusicFeatures:
        """Estimate additional audio features like danceability, energy, etc."""
        # These are simplified estimates - a real implementation would use more sophisticated methods
        
        # Danceability: Based on beat strength and tempo
        if features.tempo > 0:
            # Normalize tempo to 0-1 range (60-180 BPM)
            norm_tempo = np.clip((features.tempo - 60) / 120, 0, 1)
            # Higher tempo and more pronounced beats increase danceability
            beat_strength = np.mean(features.beats) / np.max(features.beats) if len(features.beats) > 0 else 0.5
            features.danceability = float(0.5 * norm_tempo + 0.5 * beat_strength)
        
        # Energy: Based on RMS energy
        rms = librosa.feature.rms(y=y, frame_length=self.N_FFT, hop_length=self.HOP_LENGTH)[0]
        features.energy = float(np.mean(rms) / np.max(rms) if np.max(rms) > 0 else 0.5)
        
        # Valence: Simplified based on spectral features
        # Higher spectral contrast and brightness can indicate more positive valence
        spectral_flatness = np.mean(librosa.feature.spectral_flatness(y=y))
        spectral_contrast = np.mean(features.spectral_contrast)
        features.valence = float(0.5 * spectral_flatness + 0.5 * (spectral_contrast / 10.0))
        
        # Acousticness: Based on harmonic/percussive separation
        y_harmonic, y_percussive = features.harmonic_percussive
        harmonic_ratio = np.sum(y_harmonic**2) / (np.sum(y_harmonic**2) + np.sum(y_percussive**2) + 1e-10)
        features.acousticness = float(harmonic_ratio)
        
        # Instrumentalness: Based on spectral complexity
        # More complex spectra are more likely to be instrumental
        spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=self.sample_rate))
        features.instrumentalness = float(np.clip(spectral_bandwidth / 1000.0, 0, 1))
        
        # Liveness: Based on high-frequency energy
        S = np.abs(librosa.stft(y))
        freqs = librosa.fft_frequencies(sr=self.sample_rate)
        high_freq_energy = np.mean(S[freqs > 4000, :])
        total_energy = np.mean(S)
        features.liveness = float(high_freq_energy / (total_energy + 1e-10))
        
        # Speechiness: Based on zero-crossing rate and spectral flatness
        zcr = features.zero_crossing_rate
        flatness = spectral_flatness
        features.speechiness = float(0.5 * zcr + 0.5 * flatness)
        
        return features
    
    def predict_genre(self, audio: Union[str, np.ndarray]) -> Tuple[str, float]:
        """Predict music genre from audio.
        
        Args:
            audio: Audio file path or numpy array
            
        Returns:
            Tuple of (predicted_genre, confidence)
        """
        if self.model is None:
            raise RuntimeError("No genre classification model loaded")
        
        # Load and preprocess audio
        y = self.load_audio(audio, duration=30.0)  # Use first 30 seconds
        
        # Extract features expected by the model
        # This assumes the model was trained on MFCCs with specific parameters
        mfcc = librosa.feature.mfcc(
            y=y,
            sr=self.sample_rate,
            n_mfcc=20,
            n_fft=self.N_FFT,
            hop_length=self.HOP_LENGTH
        )
        
        # Reshape for model input (add batch and channel dimensions)
        mfcc = np.expand_dims(mfcc, axis=0)
        mfcc = np.expand_dims(mfcc, axis=-1)
        
        # Predict
        predictions = self.model.predict(mfcc, verbose=0)
        predicted_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_idx])
        
        # Map index to genre
        genre = self.GENRES[predicted_idx] if predicted_idx < len(self.GENRES) else f"class_{predicted_idx}"
        
        return genre, confidence
    
    def get_beat_times(self, audio: Union[str, np.ndarray]) -> np.ndarray:
        """Get the timestamps of beats in seconds.
        
        Args:
            audio: Audio file path or numpy array
            
        Returns:
            Array of beat timestamps in seconds
        """
        y = self.load_audio(audio)
        
        # Get beat frames
        _, beat_frames = librosa.beat.beat_track(
            y=y,
            sr=self.sample_rate,
            hop_length=self.HOP_LENGTH
        )
        
        # Convert frame indices to timestamps
        return librosa.frames_to_time(
            beat_frames,
            sr=self.sample_rate,
            hop_length=self.HOP_LENGTH
        )
    
    def get_segments(self, audio: Union[str, np.ndarray], 
                    method: str = 'tempogram') -> List[Dict[str, any]]:
        """Segment audio into structural sections.
        
        Args:
            audio: Audio file path or numpy array
            method: Segmentation method ('tempogram' or 'mfcc')
            
        Returns:
            List of segment dictionaries with start/end times and labels
        """
        y = self.load_audio(audio)
        
        if method == 'tempogram':
            # Use tempogram for tempo-based segmentation
            oenv = librosa.onset.onset_strength(
                y=y,
                sr=self.sample_rate,
                hop_length=self.HOP_LENGTH
            )
            tempogram = np.abs(librosa.feature.tempogram(
                onset_envelope=oenv,
                sr=self.sample_rate,
                hop_length=self.HOP_LENGTH
            ))
            
            # Simple threshold-based segmentation
            segments = []
            threshold = np.mean(tempogram) + np.std(tempogram)
            segment_start = 0
            
            for i in range(1, tempogram.shape[1]):
                if np.any(tempogram[:, i] > threshold):
                    if i > segment_start + 1:  # Minimum segment length
                        segments.append({
                            'start': librosa.frames_to_time(segment_start, 
                                                         sr=self.sample_rate,
                                                         hop_length=self.HOP_LENGTH),
                            'end': librosa.frames_to_time(i, 
                                                       sr=self.sample_rate,
                                                       hop_length=self.HOP_LENGTH),
                            'label': 'segment'
                        })
                    segment_start = i
            
            # Add final segment
            if segment_start < tempogram.shape[1] - 1:
                segments.append({
                    'start': librosa.frames_to_time(segment_start, 
                                                  sr=self.sample_rate,
                                                  hop_length=self.HOP_LENGTH),
                    'end': librosa.frames_to_time(tempogram.shape[1], 
                                               sr=self.sample_rate,
                                               hop_length=self.HOP_LENGTH),
                    'label': 'segment'
                })
                
            return segments
            
        elif method == 'mfcc':
            # Use MFCCs and clustering for segmentation
            mfcc = librosa.feature.mfcc(
                y=y,
                sr=self.sample_rate,
                n_mfcc=13,
                hop_length=self.HOP_LENGTH
            )
            
            # Simple K-means clustering
            from sklearn.cluster import KMeans
            
            # Transpose to get frames as samples
            X = mfcc.T
            
            # Use 3-5 clusters for typical song structure (intro, verse, chorus, etc.)
            n_clusters = min(5, X.shape[0] // 10)  # At least 10 frames per cluster
            n_clusters = max(3, n_clusters)  # At least 3 clusters
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            labels = kmeans.fit_predict(X)
            
            # Convert to segments
            segments = []
            current_label = labels[0]
            segment_start = 0
            
            for i, label in enumerate(labels[1:], 1):
                if label != current_label:
                    segments.append({
                        'start': librosa.frames_to_time(segment_start * self.HOP_LENGTH, 
                                                      sr=self.sample_rate),
                        'end': librosa.frames_to_time(i * self.HOP_LENGTH, 
                                                   sr=self.sample_rate),
                        'label': f'section_{current_label}'
                    })
                    current_label = label
                    segment_start = i
            
            # Add final segment
            segments.append({
                'start': librosa.frames_to_time(segment_start * self.HOP_LENGTH, 
                                             sr=self.sample_rate),
                'end': librosa.frames_to_time(len(labels) * self.HOP_LENGTH, 
                                           sr=self.sample_rate),
                'label': f'section_{current_label}'
            })
            
            return segments
        
        else:
            raise ValueError(f"Unsupported segmentation method: {method}")

# Example usage
if __name__ == "__main__":
    # Initialize music analyzer
    analyzer = MusicAnalyzer()
    
    # Example: Extract features from a music file
    try:
        features = analyzer.extract_features("path/to/music.mp3")
        print(f"Tempo: {features.tempo:.1f} BPM")
        print(f"Key: {features.key} {features.mode}")
        print(f"Loudness: {features.loudness:.1f} dB")
        
        if features.genre:
            print(f"Predicted genre: {features.genre} (confidence: {features.genre_confidence:.2f})")
        
        # Get beat times
        beat_times = analyzer.get_beat_times("path/to/music.mp3")
        print(f"Found {len(beat_times)} beats")
        
        # Get song segments
        segments = analyzer.get_segments("path/to/music.mp3", method='mfcc')
        print(f"Found {len(segments)} segments")
        
    except Exception as e:
        print(f"Error: {e}")
