# NLP Enhancements

This module provides advanced natural language processing capabilities for the knowledge system.

## Features

- **Text Processing**: Tokenization, lemmatization, and part-of-speech tagging
- **Entity Recognition**: Identify named entities in text
- **Sentiment Analysis**: Determine sentiment (positive/negative/neutral)
- **Language Detection**: Detect the language of input text
- **Fallback Mechanisms**: Graceful degradation when dependencies are missing

## Installation

1. Install the required dependencies:
   ```bash
   pip install spacy
   python -m spacy download en_core_web_sm
   ```

## Usage

```python
from nlp_enhancements import NLPEnhancer

# Initialize the NLP enhancer
nlp = NLPEnhancer()

# Process text
result = nlp.process_text("Natural language processing is amazing!")
print(result)

# Analyze sentiment
sentiment = nlp.analyze_sentiment("I love this product!")
print(f"Sentiment: {sentiment}")

# Detect language
language = nlp.detect_language("Bonjour le monde")
print(f"Detected language: {language}")
```

## Advanced Configuration

You can specify a different spaCy model during initialization:

```python
# Use a larger English model
nlp = NLPEnhancer(model_name="en_core_web_lg")

# Or a different language model
nlp = NLPEnhancer(model_name="es_core_news_sm")  # Spanish
```

## Fallback Behavior

If spaCy is not available, the module will fall back to simpler implementations:
- Basic whitespace tokenization
- Simple rule-based sentiment analysis
- Limited language detection

## Extending Functionality

To add new NLP capabilities, extend the `NLPEnhancer` class and override the relevant methods.

## Dependencies

- Python 3.7+
- spaCy (optional, for advanced features)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
