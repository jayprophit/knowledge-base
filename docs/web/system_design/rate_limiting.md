---
id: web-system-design-rate-limiting
title: Rate Limiting in System Design
description: Comprehensive documentation on rate limiting, algorithms, implementation, and best practices
author: Knowledge Base System
created_at: 2025-07-02
updated_at: 2025-07-02
version: 1.0.0
tags:
  - rate_limiting
  - api
  - system_design
  - security
relationships:
  prerequisites: []
  successors: []
  related:
    - ../apis/rest_api.md
    - ../security/security.md
---

# Rate Limiting in System Design

## Overview

Rate limiting is a technique used to control the number of requests a client can make to a server within a specified time window. It protects APIs and backend services from abuse, ensures fair resource usage, and helps prevent denial of service (DoS) attacks.

## Common Rate Limiting Algorithms

### 1. Token Bucket
Allows a burst of requests up to a certain limit and then refills tokens at a fixed rate.

```python
class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_checked = time.time()
    def allow_request(self):
        now = time.time()
        elapsed = now - self.last_checked
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_checked = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
```

### 2. Leaky Bucket
Processes requests at a fixed rate. Excess requests are queued or dropped.

### 3. Fixed Window Counter
Counts requests in fixed time windows (e.g., 100 requests per minute).

### 4. Sliding Window Log
Tracks timestamps of each request and calculates the rate over a moving window.

## Implementation Example: Flask-Limiter
```python
from flask import Flask
from flask_limiter import Limiter
app = Flask(__name__)
limiter = Limiter(app, default_limits=["100 per hour"])
@app.route("/api/resource")
@limiter.limit("10/minute")
def resource():
    return "Resource"
```

## Best Practices
- Set sensible default and per-endpoint limits
- Return informative HTTP headers (e.g., `X-RateLimit-Remaining`)
- Use distributed stores (Redis) for rate limiting in multi-server deployments
- Provide clear error messages (HTTP 429 Too Many Requests)
- Allow for whitelisting and blacklisting

## Related Topics
- [REST API Design](../apis/rest_api.md)
- [Security](temp_reorg/docs/web/security/security.md)

## References
- [OWASP Rate Limiting](https://owasp.org/www-community/attacks/Rate_limiting)
- [Flask-Limiter Documentation](https://flask-limiter.readthedocs.io/en/stable/)
- [RFC 6585 (HTTP 429)](https://tools.ietf.org/html/rfc6585)
