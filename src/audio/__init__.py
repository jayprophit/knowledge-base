"""
Audio Processing Module

This module provides functionality for audio processing, speech recognition,
voice analysis, and sound classification.
"""

from .speech_recognition import SpeechRecognizer
from .voice_analysis import VoiceAnalyzer
from .sound_classification import SoundClassifier
from .music_analysis import MusicAnalyzer

__all__ = [
    'SpeechRecognizer',
    'VoiceAnalyzer',
    'SoundClassifier',
    'MusicAnalyzer'
]
