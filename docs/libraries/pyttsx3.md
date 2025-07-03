# pyttsx3 Library

## Overview
[pyttsx3](https://pypi.org/project/pyttsx3/) is a Python library for text-to-speech conversion. It works offline and supports multiple speech engines (SAPI5 on Windows, NSSpeechSynthesizer on Mac, and espeak on Linux).

## Installation
```sh
pip install pyttsx3
```

## Example Usage
```python
import pyttsx3
engine = pyttsx3.init()
engine.say("Hello, I am your virtual assistant.")
engine.runAndWait()
```

## Integration Notes
- Used for voice output in the virtual assistant.
- Can be paired with SpeechRecognition for full voice interaction.

## Cross-links
- [virtual_assistant_book.md](../virtual_assistant_book.md)
- [ai_agents.md](../ai_agents.md)

---
_Last updated: July 3, 2025_
