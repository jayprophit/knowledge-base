# google-api-python-client Library

## Overview
[google-api-python-client](https://github.com/googleapis/google-api-python-client) is the official Python client for Google APIs, including Gmail, Calendar, Drive, and more.

## Installation
```sh
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Example Usage
```python
from googleapiclient.discovery import build
service = build('gmail', 'v1', credentials=your_credentials)
results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
messages = results.get('messages', [])
print(messages)
```

## Integration Notes
- Used for integrating Gmail, Calendar, and other Google services in the assistant.
- Requires OAuth2 credentials setup.

## Cross-links
- [virtual_assistant_book.md](../virtual_assistant_book.md)
- [ai_agents.md](../ai_agents.md)

---
_Last updated: July 3, 2025_
