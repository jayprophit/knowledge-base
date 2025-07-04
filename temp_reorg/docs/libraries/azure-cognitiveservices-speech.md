---
author: Knowledge Base Automation System
created_at: '2025-07-04'
description: Documentation on Azure-Cognitiveservices-Speech for libraries/azure-cognitiveservices-speech.md
title: Azure-Cognitiveservices-Speech
updated_at: '2025-07-04'
version: 1.0.0
---

# azure-cognitiveservices-speech Library

## Overview
[azure-cognitiveservices-speech](https://pypi.org/project/azure-cognitiveservices-speech/) is Microsoft’s SDK for speech-to-text and text-to-speech in Python, supporting real-time and batch processing.

## Installation
```sh
pip install azure-cognitiveservices-speech
```

## Example Usage
```python
import azure.cognitiveservices.speech as speechsdk
speech_config = speechsdk.SpeechConfig(subscription="YourSubscriptionKey", region="YourServiceRegion")
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
print("Say something...")
result = speech_recognizer.recognize_once()
print("Recognized:", result.text)
```

## Integration Notes
- Used for both speech-to-text and text-to-speech in the assistant.
- Requires Azure subscription and setup.

## Cross-links
- [virtual_assistant_book.md](../virtual_assistant_book.md)
- [ai_agents.md](../ai_agents.md)

---
_Last updated: July 3, 2025_
