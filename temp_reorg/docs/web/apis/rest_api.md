---
id: web-apis-rest
title: REST API Design and Implementation
description: Comprehensive documentation on REST API principles, design best practices,
  and implementation examples
author: Knowledge Base System
created_at: 2025-07-02
updated_at: 2025-07-02
version: 1.0.0
tags:
- rest_api
- api_design
- web_services
- http
- system_design
relationships:
  prerequisites: []
  successors:
  - graphql.md
  - api_gateway.md
  related:
  - ../networking/http.md
  - graphql.md
  - api_gateway.md
  - ../security/authentication.md
---

# REST APIs

## Overview

REST (Representational State Transfer) is an architectural style for designing networked applications. RESTful APIs use HTTP requests to perform CRUD (Create, Read, Update, Delete) operations on resources. They are stateless, cacheable, and follow a client-server architecture.

## Core Principles of REST

### 1. Resource-Based
REST APIs are structured around resources, which are any kind of object, data, or service that can be uniquely identified (e.g., `/users`, `/orders`).

### 2. Statelessness
Each request from client to server must contain all information needed to understand and process the request. The server does not store client context between requests.

### 3. Uniform Interface
A consistent, standardized interface (usually HTTP) is used for all interactions.

### 4. Cacheability
Responses must define themselves as cacheable or not, to improve performance and scalability.

### 5. Layered System
A client cannot ordinarily tell whether it is connected directly to the end server or to an intermediary.

## HTTP Methods

| Method | Description             |
|--------|-------------------------|
| GET    | Retrieve a resource     |
| POST   | Create a new resource   |
| PUT    | Update a resource       |
| PATCH  | Partially update        |
| DELETE | Remove a resource       |

## Status Codes

- `200 OK`: Successful GET, PUT, PATCH, or DELETE
- `201 Created`: Successful POST
- `204 No Content`: Successful request, no body
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Not enough permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict
- `500 Internal Server Error`: Generic server error

## URL Design
- Use plural nouns: `/users`, `/orders`
- Use sub-resources for relationships: `/users/123/orders`
- Avoid verbs: `/getUser` → `/users/123`

## Query Parameters
- Filtering: `/users?role=admin`
- Sorting: `/users?sort=created_at`
- Pagination: `/users?page=2&page_size=50`

## Versioning
- URI versioning: `/v1/users`
- Header versioning: `Accept: application/vnd.example.v1+json`

## Authentication & Authorization
- Token-based (JWT, OAuth2)
- API keys
- HTTP Basic Auth
- See [../security/authentication.md](../security/authentication.md)

## Error Handling
Return structured error objects:
```json
# NOTE: The following code had syntax errors and was commented out
# # NOTE: The following code had syntax errors and was commented out
# # {
# #   "error": {
# #     "code": 400,
# #     "message": "Invalid input data"
# #   }
# # }
```

## Rate Limiting
Protects APIs from abuse by limiting the number of requests per client.

**Example (Flask-Limiter):**
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

## REST API Example: Python (FastAPI)
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    email: str

users = {}

@app.post("/users", status_code=201)
def create_user(user: User):
    if user.id in users:
        raise HTTPException(status_code=409, detail="User already exists")
    users[user.id] = user
    return user

@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

## REST API Example: Node.js (Express)
```js
const express = require('express');
const app = express();
app.use(express.json());

let users = {};

app.post('/users', (req, res) => {
  const { id, name, email } = req.body;
  if (users[id]) return res.status(409).json({ error: 'User already exists' });
  users[id] = { id, name, email };
  res.status(201).json(users[id]);
});

app.get('/users/:id', (req, res) => {
  const user = users[req.params.id];
  if (!user) return res.status(404).json({ error: 'User not found' });
  res.json(user);
});

app.listen(3000);
```

## Related Topics
- [GraphQL](graphql.md)
- [API Gateways](api_gateway.md)
- [Authentication](../security/authentication.md)
- [HTTP](../networking/http.md)
- [Rate Limiting](../system_design/rate_limiting.md)

## References
- [RESTful API Design Guidelines](https://restfulapi.net/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Express Documentation](https://expressjs.com/)
- [RFC 7231 (HTTP/1.1)](https://tools.ietf.org/html/rfc7231)
