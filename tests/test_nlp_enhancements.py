"""
Unit tests for the NLP enhancements module.
"""

import unittest
import sys
import os
from pathlib import Path

# Add the parent directory to the path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.multidisciplinary_ai.improvements.nlp_enhancements import (
    NLPEnhancer, Language, Sentiment, Entity
)

class TestNLPEnhancer(unittest.TestCase):
    """Test cases for the NLPEnhancer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.nlp = NLPEnhancer()
        self.test_text = """
        Natural language processing (NLP) is a subfield of artificial intelligence 
        that focuses on the interaction between computers and humans through natural language. 
        The ultimate objective of NLP is to read, decipher, understand, and make sense of 
        human language in a valuable way.
        """
    
    def test_process_text_basic(self):
        ""Test basic text processing."""
        result = self.nlp.process_text("Hello, world!")
        self.assertIn("tokens", result)
        self.assertIn("sentences", result)
        self.assertIn("sentiment", result)
        self.assertIn("language", result)
        
        # Should have at least one token
        self.assertGreater(len(result["tokens"]), 0)
        
        # Should have exactly one sentence for this input
        self.assertEqual(len(result["sentences"]), 1)
    
    def test_analyze_sentiment(self):
        ""Test sentiment analysis."""
        # Test positive sentiment
        pos_result = self.nlp.analyze_sentiment("I love this amazing product!")
        self.assertEqual(pos_result["label"], Sentiment.POSITIVE.value)
        self.assertGreater(pos_result["score"], 0.5)
        
        # Test negative sentiment
        neg_result = self.nlp.analyze_sentiment("This is terrible and awful!")
        self.assertEqual(neg_result["label"], Sentiment.NEGATIVE.value)
        
        # Test neutral sentiment
        neutral_result = self.nlp.analyze_sentiment("This is a test.")
        self.assertEqual(neutral_result["label"], Sentiment.NEUTRAL.value)
    
    def test_detect_language(self):
        ""Test language detection."""
        # Test English
        self.assertEqual(
            self.nlp.detect_language("This is an English sentence."),
            Language.ENGLISH
        )
        
        # Test Spanish
        self.assertEqual(
            self.nlp.detect_language("Hola, ¿cómo estás?"),
            Language.SPANISH
        )
        
        # Test French
        self.assertEqual(
            self.nlp.detect_language("Bonjour le monde"),
            Language.FRENCH
        )
        
        # Test unknown language
        self.assertEqual(
            self.nlp.detect_language("12345 67890 !@#$%"),
            Language.UNKNOWN
        )
    
    def test_entity_recognition(self):
        ""Test named entity recognition."""
        result = self.nlp.process_text("Apple is looking at buying U.K. startup for $1 billion.")
        
        # Should find at least one entity
        self.assertGreater(len(result["entities"]), 0)
        
        # Check if organization and money entities are detected
        entity_texts = [e["text"] for e in result["entities"]]
        self.assertIn("Apple", entity_texts)
        self.assertIn("U.K.", entity_texts)
        self.assertIn("$1 billion", entity_texts)
    
    def test_fallback_behavior(self):
        ""Test fallback behavior when spaCy is not available."""
        # Save the original nlp attribute
        original_nlp = self.nlp.nlp
        
        try:
            # Simulate spaCy not being available
            self.nlp.nlp = None
            
            # Test that basic processing still works
            result = self.nlp.process_text("Hello, world!")
            self.assertIn("tokens", result)
            self.assertIn("sentences", result)
            
            # Should still get sentiment analysis (using fallback)
            sentiment = self.nlp.analyze_sentiment("I love this!")
            self.assertIn(sentiment["label"], [s.value for s in Sentiment])
            
        finally:
            # Restore the original nlp attribute
            self.nlp.nlp = original_nlp
    
    def test_empty_input(self):
        ""Test handling of empty input."""
        result = self.nlp.process_text("")
        self.assertIn("error", result)
        
        sentiment = self.nlp.analyze_sentiment("")
        self.assertEqual(sentiment["label"], Sentiment.NEUTRAL.value)
        self.assertEqual(sentiment["score"], 0.5)
        
        language = self.nlp.detect_language("")
        self.assertEqual(language, Language.UNKNOWN)

if __name__ == "__main__":
    unittest.main()
