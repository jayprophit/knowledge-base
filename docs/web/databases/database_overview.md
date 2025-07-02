---
id: web-database-overview
title: Database Systems Overview
description: Comprehensive documentation on database systems, types, selection criteria, and implementation examples
author: Knowledge Base System
created_at: 2025-07-02
updated_at: 2025-07-02
version: 1.0.0
tags:
  - database
  - sql
  - nosql
  - data_storage
  - system_design
relationships:
  prerequisites: []
  successors:
    - overview.md
    - ../system_design/cache.md
    - ../performance/denormalization.md
    - ../system_design/vertical_partitioning.md
  related:
    - ../system_design/cache.md
    - ../performance/denormalization.md
    - ../system_design/vertical_partitioning.md
---

# Database Systems Overview

## Introduction

Database systems are foundational components in modern system architecture, responsible for reliable data storage, retrieval, and management. Choosing the right database solution is critical for application performance, scalability, and reliability.

## SQL vs NoSQL Databases

### SQL Databases
SQL (Structured Query Language) databases are relational database management systems that store data in structured tables with predefined schemas.

**Key Characteristics:**
- Structured data with strict schemas
- ACID transactions (Atomicity, Consistency, Isolation, Durability)
- Primary and foreign key relationships
- Complex query capabilities
- Data normalization

**Popular Systems:**
- PostgreSQL
- MySQL/MariaDB
- Oracle Database
- Microsoft SQL Server
- SQLite

**Sample Schema Definition (PostgreSQL):**
```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### NoSQL Databases
NoSQL databases use more flexible data models, designed for specific data models and have flexible schemas for building modern applications.

**Key Characteristics:**
- Schema flexibility
- Horizontal scalability
- BASE properties (Basically Available, Soft state, Eventually consistent)
- Optimized for specific data access patterns

**Types:**
- Document Stores (MongoDB, CouchDB)
- Key-Value Stores (Redis, DynamoDB)
- Column-Family Stores (Cassandra, HBase)
- Graph Databases (Neo4j, JanusGraph)

**Sample Document (MongoDB):**
```json
{
  "user_id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "created_at": "2025-07-02T16:00:00Z"
}
```

## Scaling Strategies

### Vertical Scaling
Increasing resources (CPU, RAM, storage) on a single server. Simple but limited by hardware.

### Horizontal Scaling (Sharding)
Distributing data across multiple servers (shards) to handle more load.

**Example (MongoDB Sharding):**
```javascript
sh.enableSharding("mydb")
sh.shardCollection("mydb.users", { "user_id": 1 })
```

## Replication
Replication creates and maintains copies of data across multiple database instances for redundancy and high availability.

**Types:**
- Master-Slave
- Master-Master
- Cascading

**PostgreSQL Example:**
```sql
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'password';
```

## Vertical Partitioning
Splitting a table by columns to optimize performance and security.

**Example:**
```sql
CREATE TABLE user_core (
  user_id INT PRIMARY KEY,
  username VARCHAR(50),
  email VARCHAR(100)
);
CREATE TABLE user_extended (
  user_id INT PRIMARY KEY,
  biography TEXT,
  profile_image BYTEA,
  FOREIGN KEY (user_id) REFERENCES user_core(user_id)
);
```

## Caching
Caching is used to reduce database load and improve response times. See [../system_design/cache.md](../system_design/cache.md).

## Denormalization
Adding redundant data to improve read performance at the cost of write complexity.

**Example:**
```sql
CREATE TABLE order_reports (
  order_id INT,
  user_id INT,
  username VARCHAR(50),
  order_date TIMESTAMP,
  total DECIMAL(10,2),
  PRIMARY KEY (order_id, user_id)
);
```

## CAP Theorem
A distributed database can only guarantee two of the following:
- Consistency
- Availability
- Partition Tolerance

**Examples:**
- CA: Traditional RDBMS
- CP: MongoDB (majority writes)
- AP: Cassandra

## Implementation Examples

### PostgreSQL Docker Compose
```yaml
version: '3'
services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
      POSTGRES_DB: mydb
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
volumes:
  postgres-data:
```

### Redis Cache
```yaml
version: '3'
services:
  redis:
    image: redis:6
    command: redis-server --appendonly yes
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
volumes:
  redis-data:
```

## References
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Redis Documentation](https://redis.io/documentation)
- [CAP Theorem](https://www.ibm.com/cloud/learn/cap-theorem)
- [../system_design/cache.md](../system_design/cache.md)
- [../performance/denormalization.md](../performance/denormalization.md)
- [../system_design/vertical_partitioning.md](../system_design/vertical_partitioning.md)
