"""
Audio Recognition Module

This module provides a unified interface for multi-modal audio recognition,
integrating speech recognition, voice analysis, music analysis, and sound
classification into a single comprehensive API.
"""

import os
import numpy as np
import librosa
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import logging

# Import our audio processing modules
from .speech_recognition import SpeechRecognizer, RecognitionResult
from .voice_analysis import VoiceAnalyzer, VoiceCharacteristics
from .music_analysis import MusicAnalyzer, MusicFeatures
from .sound_classification import SoundClassifier, SoundClassificationResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioRecognitionSystem:
    """Unified system for multi-modal audio recognition and analysis."""
    
    def __init__(self, 
                speech_model_path: Optional[str] = None,
                speech_scorer_path: Optional[str] = None,
                music_model_path: Optional[str] = None,
                sound_model_path: Optional[str] = None,
                sound_class_map_path: Optional[str] = None):
        """Initialize the audio recognition system with optional models.
        
        Args:
            speech_model_path: Path to DeepSpeech model for speech recognition
            speech_scorer_path: Path to DeepSpeech scorer for speech recognition
            music_model_path: Path to music genre classification model
            sound_model_path: Path to environmental sound classification model
            sound_class_map_path: Path to sound class mapping file
        """
        # Initialize component recognizers
        self.speech_recognizer = SpeechRecognizer(
            model_path=speech_model_path,
            scorer_path=speech_scorer_path
        )
        
        self.voice_analyzer = VoiceAnalyzer()
        
        self.music_analyzer = MusicAnalyzer(
            model_path=music_model_path
        )
        
        self.sound_classifier = SoundClassifier(
            model_path=sound_model_path
        )
        
        # Load sound class map if provided
        if sound_model_path and sound_class_map_path:
            self.sound_classifier.load_model(sound_model_path, sound_class_map_path)
            
        logger.info("Audio Recognition System initialized")
    
    def identify_audio_type(self, audio_file: str) -> str:
        """Identify the type of audio (speech, music, or environmental sound).
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Audio type as string: 'speech', 'music', 'environmental', or 'unknown'
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_file, sr=22050, duration=10)
            
            # Extract features for classification
            # Simple approach: compare energy in speech vs music frequency ranges
            
            # Speech typically has energy concentrated in 250-2500 Hz
            fft = np.abs(librosa.stft(y))
            freqs = librosa.fft_frequencies(sr=sr)
            speech_mask = (freqs >= 250) & (freqs <= 2500)
            speech_energy = np.mean(fft[speech_mask, :])
            
            # Music typically has more regular structure and wider frequency range
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            mfcc_var = np.var(mfcc, axis=1).sum()
            
            # Environmental sounds often have less tonal content
            zcr = librosa.feature.zero_crossing_rate(y)
            zcr_mean = np.mean(zcr)
            
            # Simple rule-based classification
            if tempo > 0 and mfcc_var > 100:
                return 'music'
            elif speech_energy > 0.01 and zcr_mean < 0.1:
                return 'speech'
            else:
                return 'environmental'
                
        except Exception as e:
            logger.error(f"Error identifying audio type: {e}")
            return 'unknown'
    
    def process_audio(self, audio_file: str, extract_all: bool = False) -> Dict[str, Any]:
        """Process audio file with the appropriate recognition method based on content.
        
        Args:
            audio_file: Path to audio file
            extract_all: Whether to extract all features regardless of audio type
            
        Returns:
            Dictionary with recognition results
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
            
        # Identify audio type
        audio_type = self.identify_audio_type(audio_file)
        
        # Initialize results dictionary
        results = {
            'audio_file': audio_file,
            'audio_type': audio_type,
            'speech_recognition': None,
            'voice_analysis': None,
            'music_analysis': None,
            'sound_classification': None
        }
        
        # Process based on identified type or extract all if requested
        try:
            if audio_type == 'speech' or extract_all:
                # Speech recognition
                speech_result = self.speech_recognizer.recognize_google(audio_file)
                results['speech_recognition'] = {
                    'text': speech_result.text,
                    'confidence': speech_result.confidence
                }
                
                # Voice analysis
                try:
                    features = self.voice_analyzer.extract_features(audio_file)
                    results['voice_analysis'] = {
                        'pitch': features.pitch_hz,
                        'gender': features.gender,
                        'speaking_rate': features.speaking_rate,
                        'intensity': features.intensity_db
                    }
                except Exception as e:
                    logger.warning(f"Voice analysis failed: {e}")
            
            if audio_type == 'music' or extract_all:
                # Music analysis
                try:
                    features = self.music_analyzer.extract_features(audio_file)
                    results['music_analysis'] = {
                        'tempo': features.tempo,
                        'key': features.key,
                        'mode': features.mode,
                        'genre': features.genre,
                        'danceability': features.danceability,
                        'energy': features.energy
                    }
                except Exception as e:
                    logger.warning(f"Music analysis failed: {e}")
            
            if audio_type == 'environmental' or extract_all:
                # Sound classification
                try:
                    if self.sound_classifier.model:
                        sound_result = self.sound_classifier.classify_sound(audio_file)
                        results['sound_classification'] = {
                            'label': sound_result.label,
                            'confidence': sound_result.confidence,
                            'category': sound_result.category,
                            'top_predictions': sound_result.top_predictions
                        }
                except Exception as e:
                    logger.warning(f"Sound classification failed: {e}")
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            results['error'] = str(e)
        
        return results
    
    def recognize_from_microphone(self, duration: int = 5) -> Dict[str, Any]:
        """Record audio from microphone and recognize content.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Dictionary with recognition results
        """
        try:
            # Record audio using speech recognizer
            speech_result = self.speech_recognizer.recognize_from_microphone(duration)
            
            results = {
                'audio_type': 'microphone_recording',
                'speech_recognition': {
                    'text': speech_result.text,
                    'confidence': speech_result.confidence
                }
            }
            
            # If no speech was detected, inform the user
            if not speech_result.text:
                results['status'] = 'No speech detected'
                
            return results
            
        except Exception as e:
            logger.error(f"Error recording from microphone: {e}")
            return {
                'audio_type': 'microphone_recording',
                'error': str(e)
            }
    
    def detect_language(self, text: str) -> str:
        """Detect language of text using transformers.
        
        Args:
            text: Input text for language detection
            
        Returns:
            Detected language code
        """
        try:
            # Check if text is empty
            if not text:
                return 'unknown'
                
            # Use transformers pipeline for language detection
            try:
                from transformers import pipeline
                language_identifier = pipeline("text-classification", 
                                             model="papluca/xlm-roberta-base-language-detection")
                result = language_identifier(text)
                return result[0]['label']
            except ImportError:
                # Fallback to basic language detection
                # This is a very simplified version
                english_freq = ['the', 'and', 'to', 'of', 'a', 'in', 'that', 'is']
                spanish_freq = ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'ser']
                french_freq = ['le', 'la', 'de', 'et', 'un', 'une', 'en', 'que']
                
                text = text.lower()
                en_count = sum(word in text for word in english_freq)
                es_count = sum(word in text for word in spanish_freq)
                fr_count = sum(word in text for word in french_freq)
                
                if en_count > es_count and en_count > fr_count:
                    return 'en'
                elif es_count > en_count and es_count > fr_count:
                    return 'es'
                elif fr_count > en_count and fr_count > es_count:
                    return 'fr'
                else:
                    return 'unknown'
                    
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return 'unknown'


# Example usage
if __name__ == "__main__":
    # Initialize the audio recognition system
    system = AudioRecognitionSystem()
    
    try:
        # Process an audio file
        # results = system.process_audio("path/to/audio.wav")
        # print(f"Audio type: {results['audio_type']}")
        
        # # If speech was detected
        # if results['speech_recognition'] and results['speech_recognition']['text']:
        #     text = results['speech_recognition']['text']
        #     print(f"Transcription: {text}")
        #     
        #     # Detect language
        #     language = system.detect_language(text)
        #     print(f"Detected language: {language}")
        
        print("Audio Recognition System loaded successfully")
        
    except Exception as e:
        print(f"Error: {e}")
