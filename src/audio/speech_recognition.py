"""
Speech Recognition Module

This module provides functionality for automatic speech recognition (ASR)
using various backends including DeepSpeech and Google Speech Recognition.
"""

import os
import wave
import numpy as np
import speech_recognition as sr
from dataclasses import dataclass
from typing import Optional, Union, List, Dict, Any
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RecognitionResult:
    """Data class to store speech recognition results."""
    text: str
    confidence: Optional[float] = None
    language: Optional[str] = None
    alternatives: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None

class SpeechRecognizer:
    """Speech recognition using multiple backends."""
    
    def __init__(self, model_path: Optional[str] = None, scorer_path: Optional[str] = None):
        """Initialize the speech recognizer.
        
        Args:
            model_path: Path to the DeepSpeech model file (.pbmm)
            scorer_path: Path to the DeepSpeech scorer file (.scorer)
        """
        self.model_path = model_path
        self.scorer_path = scorer_path
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300  # Adjust based on your microphone
        self.recognizer.dynamic_energy_threshold = True
        
        # Initialize DeepSpeech if model is provided
        self.ds_model = None
        if model_path and os.path.exists(model_path):
            self._init_deepspeech(model_path, scorer_path)
    
    def _init_deepspeech(self, model_path: str, scorer_path: Optional[str] = None):
        """Initialize the DeepSpeech model."""
        try:
            import deepspeech
            self.ds_model = deepspeech.Model(model_path)
            
            if scorer_path and os.path.exists(scorer_path):
                self.ds_model.enableExternalScorer(scorer_path)
                
            logger.info(f"Loaded DeepSpeech model from {model_path}")
            if scorer_path:
                logger.info(f"Loaded DeepSpeech scorer from {scorer_path}")
                
        except ImportError:
            logger.warning("DeepSpeech not installed. Install with: pip install deepspeech")
        except Exception as e:
            logger.error(f"Failed to initialize DeepSpeech: {e}")
    
    def recognize_google(self, audio_data: Union[str, sr.AudioData], 
                        language: str = "en-US", 
                        show_all: bool = False) -> RecognitionResult:
        """Recognize speech using Google Web Speech API.
        
        Args:
            audio_data: Audio data or path to audio file
            language: Language code (e.g., 'en-US', 'es-ES')
            show_all: Whether to return all possible results
            
        Returns:
            RecognitionResult object with the recognized text and metadata
        """
        try:
            if isinstance(audio_data, str):
                with sr.AudioFile(audio_data) as source:
                    audio = self.recognizer.record(source)
            else:
                audio = audio_data
            
            result = self.recognizer.recognize_google(
                audio, 
                language=language,
                show_all=show_all
            )
            
            if show_all and isinstance(result, dict):
                # Handle full result with alternatives
                return RecognitionResult(
                    text=result['alternative'][0]['transcript'],
                    confidence=result['alternative'][0].get('confidence'),
                    language=language,
                    alternatives=[
                        {'text': alt['transcript'], 'confidence': alt.get('confidence')}
                        for alt in result.get('alternative', [])[1:]
                    ],
                    metadata={'api': 'google', 'raw': result}
                )
            else:
                return RecognitionResult(
                    text=result if isinstance(result, str) else "",
                    language=language,
                    metadata={'api': 'google'}
                )
                
        except sr.UnknownValueError:
            return RecognitionResult(
                text="",
                confidence=0.0,
                language=language,
                metadata={'error': 'Could not understand audio', 'api': 'google'}
            )
        except sr.RequestError as e:
            return RecognitionResult(
                text="",
                confidence=0.0,
                language=language,
                metadata={'error': str(e), 'api': 'google'}
            )
    
    def recognize_deepspeech(self, audio_data: Union[str, np.ndarray, sr.AudioData],
                           sample_rate: int = 16000) -> RecognitionResult:
        """Recognize speech using Mozilla DeepSpeech.
        
        Args:
            audio_data: Audio data, file path, or AudioData object
            sample_rate: Sample rate of the audio (only used if audio_data is numpy array)
            
        Returns:
            RecognitionResult object with the recognized text
        """
        if self.ds_model is None:
            raise RuntimeError("DeepSpeech model not initialized. Provide model_path during initialization.")
        
        try:
            # Handle different input types
            if isinstance(audio_data, str):
                # Load from file
                if not os.path.exists(audio_data):
                    raise FileNotFoundError(f"Audio file not found: {audio_data}")
                
                with wave.open(audio_data, 'rb') as wav_file:
                    sample_rate = wav_file.getframerate()
                    audio = np.frombuffer(wav_file.readframes(wav_file.getnframes()), 
                                        np.int16)
            elif isinstance(audio_data, sr.AudioData):
                # Convert from SpeechRecognition AudioData
                audio = np.frombuffer(audio_data.get_raw_data(), 
                                    dtype=np.int16)
                sample_rate = audio_data.sample_rate
            elif isinstance(audio_data, np.ndarray):
                audio = audio_data.astype(np.int16)
            else:
                raise ValueError("audio_data must be file path, AudioData, or numpy array")
            
            # Resample if needed
            if sample_rate != 16000:
                import librosa
                audio = librosa.resample(
                    audio.astype(np.float32) / 32768.0,  # Convert to float
                    orig_sr=sample_rate,
                    target_sr=16000
                )
                audio = (audio * 32768.0).astype(np.int16)
            
            # Perform speech recognition
            text = self.ds_model.stt(audio)
            
            return RecognitionResult(
                text=text,
                language="en-US",  # DeepSpeech models are language-specific
                metadata={'api': 'deepspeech'}
            )
            
        except Exception as e:
            logger.error(f"DeepSpeech recognition error: {e}")
            return RecognitionResult(
                text="",
                confidence=0.0,
                metadata={'error': str(e), 'api': 'deepspeech'}
            )
    
    def recognize_from_microphone(self, duration: int = 5, language: str = "en-US") -> RecognitionResult:
        """Record audio from microphone and recognize speech.
        
        Args:
            duration: Maximum duration to record (seconds)
            language: Language code for recognition
            
        Returns:
            RecognitionResult object with the recognized text
        """
        try:
            with sr.Microphone() as source:
                logger.info("Listening... (speak now)")
                audio = self.recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
                
                # Try Google first, fall back to DeepSpeech if available
                try:
                    return self.recognize_google(audio, language=language)
                except Exception as e:
                    logger.warning(f"Google recognition failed: {e}")
                    if self.ds_model:
                        return self.recognize_deepspeech(audio)
                    raise
                    
        except sr.WaitTimeoutError:
            return RecognitionResult(
                text="",
                confidence=0.0,
                language=language,
                metadata={'error': 'No speech detected', 'api': 'microphone'}
            )
        except Exception as e:
            return RecognitionResult(
                text="",
                confidence=0.0,
                language=language,
                metadata={'error': str(e), 'api': 'microphone'}
            )
    
    @staticmethod
    def save_audio(audio_data: sr.AudioData, filename: str) -> bool:
        """Save audio data to a WAV file.
        
        Args:
            audio_data: AudioData object from SpeechRecognition
            filename: Output filename (should end with .wav)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, 'wb') as f:
                f.write(audio_data.get_wav_data())
            return True
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            return False

# Example usage
if __name__ == "__main__":
    # Initialize with DeepSpeech model (optional)
    recognizer = SpeechRecognizer()
    
    # Record from microphone
    print("Speak something...")
    result = recognizer.recognize_from_microphone(duration=5)
    
    if result.text:
        print(f"You said: {result.text}")
    else:
        print("Could not understand audio")
    
    # Recognize from file
    # result = recognizer.recognize_google("path/to/audio.wav")
    # if recognizer.ds_model:
    #     result = recognizer.recognize_deepspeech("path/to/audio.wav")
