# yagmail Library

## Overview
[yagmail](https://pypi.org/project/yagmail/) is a Python library that makes sending emails easy and secure, especially with Gmail.

## Installation
```sh
pip install yagmail
```

## Example Usage
```python
import yagmail
yag = yagmail.SMTP('your@gmail.com')
yag.send('to@domain.com', 'subject', 'body')
```

## Integration Notes
- Used for sending emails in the assistant.
- Can be combined with scheduling and automation modules.

## Cross-links
- [virtual_assistant_book.md](../virtual_assistant_book.md)
- [ai_agents.md](../ai_agents.md)

---
_Last updated: July 3, 2025_
