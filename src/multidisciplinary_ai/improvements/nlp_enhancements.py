"""
NLP Enhancements
===============

Core NLP capabilities for the knowledge system including:
- Text processing
- Sentiment analysis
- Entity recognition
- Text summarization
- Language detection
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Language(Enum):
    """Supported languages for NLP processing."""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    RUSSIAN = "ru"
    UNKNOWN = "unk"

class Sentiment(Enum):
    """Sentiment classification."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

@dataclass
class Entity:
    """Named entity in text."""
    text: str
    entity_type: str
    start: int
    end: int
    confidence: float = 1.0

class NLPEnhancer:
    """
    Enhanced NLP processing capabilities.
    Uses spaCy under the hood with fallbacks.
    """
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize the NLP enhancer."""
        self.model_name = model_name
        self.nlp = self._load_nlp_model()
        
    def _load_nlp_model(self):
        """Load the NLP model."""
        try:
            import spacy
            nlp = spacy.load(self.model_name)
            logger.info(f"Loaded spaCy model: {self.model_name}")
            return nlp
        except ImportError:
            logger.warning("spaCy not installed. Using limited functionality.")
            return None
            
    def process_text(self, text: str) -> Dict[str, Any]:
        """
        Process text with NLP pipeline.
        
        Args:
            text: Input text to process
            
        Returns:
            Dictionary with processed results
        """
        if not text or not text.strip():
            return {"error": "Empty input text"}
            
        if not self.nlp:
            return self._fallback_process(text)
            
        try:
            doc = self.nlp(text)
            
            # Extract tokens
            tokens = [{
                "text": token.text,
                "lemma": token.lemma_,
                "pos": token.pos_,
                "is_stop": token.is_stop,
                "is_punct": token.is_punct
            } for token in doc]
            
            # Extract entities
            entities = [{
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            } for ent in doc.ents]
            
            # Get sentences
            sentences = [sent.text for sent in doc.sents]
            
            # Basic sentiment (spaCy doesn't have built-in sentiment)
            sentiment = self.analyze_sentiment(text)
            
            return {
                "tokens": tokens,
                "entities": entities,
                "sentences": sentences,
                "sentiment": sentiment,
                "language": self.detect_language(text).value
            }
            
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            return self._fallback_process(text)
    
    def _fallback_process(self, text: str) -> Dict[str, Any]:
        """Fallback text processing when NLP is not available."""
        # Simple whitespace tokenization
        tokens = text.split()
        
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Basic sentiment
        sentiment = self.analyze_sentiment(text)
        
        # Simple language detection
        language = self.detect_language(text)
        
        return {
            "tokens": [{"text": t} for t in tokens],
            "sentences": sentences,
            "sentiment": sentiment,
            "language": language.value,
            "entities": []
        }
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of the text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with sentiment analysis
        """
        if not text:
            return {"label": Sentiment.NEUTRAL.value, "score": 0.5}
            
        # Simple rule-based sentiment as fallback
        positive_words = {"good", "great", "excellent", "wonderful", "amazing"}
        negative_words = {"bad", "terrible", "awful", "poor", "horrible"}
        
        words = set(text.lower().split())
        pos_count = len(words & positive_words)
        neg_count = len(words & negative_words)
        
        if pos_count > neg_count:
            return {"label": Sentiment.POSITIVE.value, "score": 0.7}
        elif neg_count > pos_count:
            return {"label": Sentiment.NEGATIVE.value, "score": 0.7}
        else:
            return {"label": Sentiment.NEUTRAL.value, "score": 0.5}
    
    def detect_language(self, text: str) -> Language:
        """
        Detect the language of the text.
        
        Args:
            text: Input text
            
        Returns:
            Detected language
        """
        if not text:
            return Language.UNKNOWN
            
        # Simple language detection based on common words
        common_words = {
            Language.ENGLISH: {"the", "be", "to", "of", "and"},
            Language.SPANISH: {"el", "la", "de", "que", "y"},
            Language.FRENCH: {"le", "la", "de", "et", "les"},
            Language.GERMAN: {"der", "die", "und", "in", "den"},
            Language.CHINESE: {"的", "一", "是", "在", "我"},
            Language.JAPANESE: {"の", "に", "は", "を", "た"},
            Language.KOREAN: {"이", "있", "하", "는", "을"},
            Language.RUSSIAN: {"и", "в", 
}}