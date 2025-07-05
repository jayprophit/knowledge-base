"""
Voice Analysis Module

This module provides functionality for voice analysis including speaker identification,
voice characteristics extraction, and voice activity detection.
"""

import os
import numpy as np
import librosa
import soundfile as sf
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Union
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VoiceCharacteristics:
    """Data class to store voice characteristics."""
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

class VoiceAnalyzer:
    """Class for analyzing voice characteristics and performing speaker identification."""
    
    def __init__(self, sample_rate: int = 16000, frame_length: int = 2048, hop_length: int = 512):
        """Initialize the voice analyzer.
        
        Args:
            sample_rate: Sample rate for audio processing
            frame_length: Length of the analysis window in samples
            hop_length: Hop length between analysis windows
        """
        self.sample_rate = sample_rate
        self.frame_length = frame_length
        self.hop_length = hop_length
        self.speaker_profiles = {}
    
    def load_audio(self, audio_path: Union[str, np.ndarray], 
                  target_sr: Optional[int] = None) -> Tuple[np.ndarray, int]:
        """Load audio from file or numpy array with optional resampling.
        
        Args:
            audio_path: Path to audio file or numpy array of audio samples
            target_sr: Target sample rate (None to keep original)
            
        Returns:
            Tuple of (audio_samples, sample_rate)
        """
        target_sr = target_sr or self.sample_rate
        
        if isinstance(audio_path, (str, Path)):
            audio, sr = librosa.load(audio_path, sr=target_sr)
        elif isinstance(audio_path, np.ndarray):
            audio = audio_path
            sr = self.sample_rate
            
            # Resample if needed
            if target_sr and sr != target_sr:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
                sr = target_sr
        else:
            raise ValueError("audio_path must be a file path or numpy array")
        
        # Convert to mono if needed
        if len(audio.shape) > 1:
            audio = librosa.to_mono(audio)
            
        return audio, sr
    
    def extract_features(self, audio: np.ndarray, sr: Optional[int] = None) -> VoiceCharacteristics:
        """Extract voice characteristics from audio.
        
        Args:
            audio: Audio samples
            sr: Sample rate (if None, use self.sample_rate)
            
        Returns:
            VoiceCharacteristics object with extracted features
        """
        sr = sr or self.sample_rate
        
        # Ensure audio is float32
        audio = audio.astype(np.float32)
        
        # Extract pitch using Pyin (more accurate than YIN for speech)
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio,
            fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7'),
            sr=sr,
            frame_length=self.frame_length,
            hop_length=self.hop_length
        )
        
        # Calculate pitch statistics (only for voiced segments)
        voiced_f0 = f0[voiced_flag > 0]
        pitch_hz = np.mean(voiced_f0) if len(voiced_f0) > 0 else 0.0
        pitch_std = np.std(voiced_f0) if len(voiced_f0) > 0 else 0.0
        
        # Calculate intensity (RMS energy in dB)
        rms_energy = librosa.feature.rms(
            y=audio,
            frame_length=self.frame_length,
            hop_length=self.hop_length
        )[0]
        intensity_db = 20 * np.log10(np.mean(rms_energy) + 1e-10)  # Avoid log(0)
        
        # Estimate speaking rate (syllables per second)
        # This is a simplified estimation
        speech_frames = librosa.effects.split(audio, top_db=30)
        speaking_rate = len(speech_frames) / (len(audio) / sr) if len(speech_frames) > 0 else 0.0
        
        # Calculate harmonics-to-noise ratio (HNR)
        hnr = self._calculate_hnr(audio, sr)
        
        # Extract MFCCs
        mfcc = librosa.feature.mfcc(
            y=audio,
            sr=sr,
            n_mfcc=13,
            n_fft=self.frame_length,
            hop_length=self.hop_length
        )
        
        # Spectral features
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(
            y=audio, sr=sr, n_fft=self.frame_length, hop_length=self.hop_length))
            
        spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(
            y=audio, sr=sr, n_fft=self.frame_length, hop_length=self.hop_length))
            
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(
            y=audio, sr=sr, n_fft=self.frame_length, hop_length=self.hop_length))
        
        # Zero-crossing rate
        zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(
            y=audio, frame_length=self.frame_length, hop_length=self.hop_length))
        
        # Estimate gender based on pitch (simplified)
        gender = self._estimate_gender(pitch_hz)
        
        return VoiceCharacteristics(
            pitch_hz=float(pitch_hz),
            pitch_std=float(pitch_std),
            intensity_db=float(intensity_db),
            speaking_rate=float(speaking_rate),
            hnr=float(hnr),
            mfcc=np.mean(mfcc, axis=1),  # Average over time
            spectral_centroid=float(spectral_centroid),
            spectral_bandwidth=float(spectral_bandwidth),
            spectral_rolloff=float(spectral_rolloff),
            zero_crossing_rate=float(zero_crossing_rate),
            gender=gender
        )
    
    def _calculate_hnr(self, audio: np.ndarray, sr: int) -> float:
        """Calculate harmonics-to-noise ratio (HNR)."""
        try:
            import parselmouth
            sound = parselmouth.Sound(audio, sampling_frequency=sr)
            harmonicity = sound.to_harmonicity()
            return float(np.nanmean(harmonicity.values[harmonicity.values != -200]))
        except ImportError:
            # Fallback to simpler method if parselmouth is not available
            logger.warning("parselmouth not installed. Using simpler HNR estimation.")
            # This is a simplified HNR estimation
            f0 = librosa.yin(
                audio,
                fmin=librosa.note_to_hz('C2'),
                fmax=librosa.note_to_hz('C7'),
                sr=sr,
                frame_length=self.frame_length,
                hop_length=self.hop_length
            )
            f0 = f0[f0 > 0]  # Remove unvoiced frames
            return float(np.mean(f0) / np.std(f0)) if len(f0) > 0 else 0.0
    
    def _estimate_gender(self, pitch_hz: float) -> Optional[str]:
        """Estimate speaker gender based on pitch (simplified)."""
        if pitch_hz == 0:
            return None
        return "male" if pitch_hz < 165 else "female"
    
    def create_speaker_profile(self, audio: Union[str, np.ndarray], 
                             speaker_id: str, 
                             sr: Optional[int] = None) -> Dict[str, any]:
        """Create a speaker profile from audio.
        
        Args:
            audio: Audio samples or path to audio file
            speaker_id: Unique identifier for the speaker
            sr: Sample rate (if None, use self.sample_rate)
            
        Returns:
            Dictionary containing the speaker profile
        """
        audio, sr = self.load_audio(audio, sr)
        features = self.extract_features(audio, sr)
        
        profile = {
            'speaker_id': speaker_id,
            'features': features,
            'mfcc_mean': np.mean(features.mfcc, axis=0).tolist(),
            'mfcc_std': np.std(features.mfcc, axis=0).tolist(),
            'pitch_mean': features.pitch_hz,
            'pitch_std': features.pitch_std,
            'gender': features.gender,
            'sample_rate': sr
        }
        
        self.speaker_profiles[speaker_id] = profile
        return profile
    
    def identify_speaker(self, audio: Union[str, np.ndarray], 
                        sr: Optional[int] = None,
                        top_n: int = 1) -> List[Dict[str, any]]:
        """Identify the most likely speaker from a set of known profiles.
        
        Args:
            audio: Audio samples or path to audio file
            sr: Sample rate (if None, use self.sample_rate)
            top_n: Number of top matches to return
            
        Returns:
            List of dictionaries with speaker IDs and similarity scores,
            ordered by descending similarity
        """
        if not self.speaker_profiles:
            raise ValueError("No speaker profiles available for comparison")
        
        audio, sr = self.load_audio(audio, sr)
        features = self.extract_features(audio, sr)
        
        # Calculate similarity to each known speaker
        similarities = []
        query_mfcc = np.mean(features.mfcc, axis=0)
        
        for speaker_id, profile in self.speaker_profiles.items():
            # Simple MFCC cosine similarity
            ref_mfcc = np.array(profile['mfcc_mean'])
            similarity = np.dot(query_mfcc, ref_mfcc) / (
                np.linalg.norm(query_mfcc) * np.linalg.norm(ref_mfcc) + 1e-10)
            
            # Adjust similarity based on pitch similarity
            pitch_similarity = 1.0 / (1.0 + abs(features.pitch_hz - profile['pitch_mean']) / 50.0)
            
            # Combined score (weighted average)
            combined_score = 0.7 * similarity + 0.3 * pitch_similarity
            
            similarities.append({
                'speaker_id': speaker_id,
                'similarity': float(combined_score),
                'mfcc_similarity': float(similarity),
                'pitch_similarity': float(pitch_similarity),
                'gender': profile['gender']
            })
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similarities[:top_n]
    
    def detect_voice_activity(self, audio: Union[str, np.ndarray], 
                            sr: Optional[int] = None,
                            threshold_db: float = 30.0) -> List[Tuple[float, float]]:
        """Detect voice activity regions in the audio.
        
        Args:
            audio: Audio samples or path to audio file
            sr: Sample rate (if None, use self.sample_rate)
            threshold_db: Threshold in dB for voice activity detection
            
        Returns:
            List of (start_time, end_time) tuples in seconds
        """
        audio, sr = self.load_audio(audio, sr)
        
        # Split audio into non-silent chunks
        non_silent = librosa.effects.split(
            audio,
            top_db=threshold_db,
            frame_length=self.frame_length,
            hop_length=self.hop_length
        )
        
        # Convert frame indices to time
        return [(start/sr, end/sr) for start, end in non_silent]
    
    def save_speaker_profile(self, speaker_id: str, filepath: str) -> bool:
        """Save a speaker profile to disk."""
        if speaker_id not in self.speaker_profiles:
            raise ValueError(f"No profile found for speaker: {speaker_id}")
        
        try:
            import json
            import numpy as np
            
            # Convert numpy arrays to lists for JSON serialization
            profile = self.speaker_profiles[speaker_id].copy()
            
            with open(filepath, 'w') as f:
                json.dump(profile, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save speaker profile: {e}")
            return False
    
    def load_speaker_profile(self, filepath: str) -> str:
        """Load a speaker profile from disk."""
        try:
            import json
            
            with open(filepath, 'r') as f:
                profile = json.load(f)
            
            speaker_id = profile['speaker_id']
            self.speaker_profiles[speaker_id] = profile
            return speaker_id
        except Exception as e:
            logger.error(f"Failed to load speaker profile: {e}")
            raise

# Example usage
if __name__ == "__main__":
    # Initialize voice analyzer
    analyzer = VoiceAnalyzer()
    
    # Example: Create speaker profile
    try:
        profile = analyzer.create_speaker_profile(
            "path/to/speaker1.wav",
            "speaker1"
        )
        print(f"Created profile for {profile['speaker_id']}")
        
        # Save profile
        analyzer.save_speaker_profile("speaker1", "speaker1_profile.json")
        
        # Identify speaker
        result = analyzer.identify_speaker("path/to/unknown.wav")
        print(f"Most likely speaker: {result[0]['speaker_id']} (confidence: {result[0]['similarity']:.2f})")
        
    except Exception as e:
        print(f"Error: {e}")
