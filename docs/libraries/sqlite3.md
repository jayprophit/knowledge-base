# sqlite3 Library

## Overview
[sqlite3](https://docs.python.org/3/library/sqlite3.html) is the built-in Python library for SQLite, a lightweight disk-based database that doesn’t require a separate server process.

## Installation
No installation needed; included with Python standard library.

## Example Usage
```python
import sqlite3
conn = sqlite3.connect('example.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)''')
c.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
conn.commit()
for row in c.execute('SELECT * FROM users'):
    print(row)
conn.close()
```

## Integration Notes
- Used for persistent storage in the assistant.
- Suitable for lightweight, local databases.

## Cross-links
- [virtual_assistant_book.md](../virtual_assistant_book.md)

---
_Last updated: July 3, 2025_
