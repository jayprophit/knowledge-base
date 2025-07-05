---
id: web-databases-overview
title: Database Systems - Overview and Comparison
description: Comprehensive documentation on database systems, including SQL vs. NoSQL
  databases, scaling strategies, and implementation examples
author: Knowledge Base System
created_at: 2025-07-02
updated_at: 2025-07-02
version: 1.0.0
tags:
- system_design
- databases
- sql
- nosql
- data_storage
relationships:
  prerequisites: []
  successors: []
  related:
  - ../system_design/cache.md
  - ../scalability/replication.md
  - ../scalability/sharding.md
---

# Database Systems Overview

## Introduction

Database systems are foundational components in modern system architecture, responsible for reliable data storage, retrieval, and management. Choosing the right database solution is critical for application performance, scalability, and reliability.

## SQL vs NoSQL Databases

### SQL Databases

SQL (Structured Query Language) databases are relational database management systems that store data in structured tables with predefined schemas.

**Key Characteristics:**
- **Structured Data**: Enforces schema for data integrity
- **ACID Compliance**: Atomicity, Consistency, Isolation, Durability
- **Relationships**: Supports complex relationships through foreign keys and joins
- **Mature Ecosystem**: Established tools, standards, and best practices
- **Standardized Language**: SQL provides a common interface across implementations

**Popular SQL Databases:**
- PostgreSQL
- MySQL
- Microsoft SQL Server
- Oracle Database
- SQLite

**Use Cases:**
- Financial systems requiring transaction support
- Applications with complex querying needs
- Systems with well-defined, stable schemas
- Data with clear relational structures

### NoSQL Databases

NoSQL databases use more flexible data models, designed for specific data models and have flexible schemas for building modern applications.

**Key Characteristics:**
- **Schema Flexibility**: Dynamic schemas for unstructured data
- **Horizontal Scalability**: Designed to scale out rather than up
- **Specialized for Use Cases**: Different types for different purposes
- **BASE Properties**: Basically Available, Soft state, Eventually consistent
- **Performance Optimization**: Often optimized for specific data access patterns

**Types of NoSQL Databases:**

1. **Document Stores**
   - Store data in document formats (JSON, BSON, XML)
   - Examples: MongoDB, CouchDB, Firestore
   - Use cases: Content management, catalogs, user profiles

2. **Key-Value Stores**
   - Simple key-value pairs with high performance
   - Examples: Redis, DynamoDB, etcd
   - Use cases: Caching, session storage, real-time data

3. **Column-Family Stores**
   - Store data in column families rather than rows
   - Examples: Cassandra, HBase, ScyllaDB
   - Use cases: Time-series data, IoT data, analytics

4. **Graph Databases**
   - Specialize in managing highly connected data
   - Examples: Neo4j, Amazon Neptune, JanusGraph
   - Use cases: Social networks, recommendation engines, fraud detection

## SQL vs NoSQL: Comparison Table

| Feature | SQL | NoSQL |
|---------|-----|-------|
| Data Structure | Tables with fixed rows and columns | Various (documents, key-value, graphs) |
| Schema | Fixed schema, rigid | Dynamic schema, flexible |
| Scalability | Primarily vertical | Primarily horizontal |
| ACID Compliance | Strong | Varies (typically sacrificed for performance) |
| Relationships | Built-in support | Limited or application-managed |
| Query Language | Standardized SQL | Database-specific APIs |
| Transaction Support | Strong | Limited in most implementations |
| Consistency | Strong consistency | Various models (strong to eventual) |
| Use Cases | Complex transactions, reporting | High throughput, unstructured data |

## Database Scaling Strategies

### Vertical Scaling

Vertical scaling (scaling up) involves increasing resources on a single server.

**Advantages:**
- Simpler implementation
- No data distribution challenges
- Full ACID compliance preserved
- No application changes required

**Disadvantages:**
- Hardware limitations
- Single point of failure
- Cost increases non-linearly
- Downtime for upgrades

**Implementation:**
```python
# NOTE: The following code had syntax errors and was commented out
# # NOTE: The following code had syntax errors and was commented out
# # # Example: Vertical scaling in a cloud environment (AWS CLI)
# # aws rds modify-db-instance \
# #     --db-instance-identifier mydbinstance \
# #     --db-instance-class db.m5.4xlarge \
# #     --apply-immediately
```

### Replication

Replication creates and maintains copies of data across multiple database instances.

**Types:**
- **Master-Slave Replication**: Writes go to master, reads can be distributed
- **Master-Master Replication**: Writes can go to multiple masters
- **Cascading Replication**: # NOTE: The following code had syntax errors and was commented out
# -- On primary server
# ALTER SYSTEM SET wal_level = replica;
# ALTER SYSTEM SET max_wal_senders = 10;
# ALTER SYSTEM SET max_replication_slots = 10;
# 
# -- Create replication user
# CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'strongpassword';
# 
# -- On replica server
# -- In postgresql.conf
# primary_conninfo = 'host=primary.example.com port=# NOTE: The following code had syntax errors and was commented out
# -- On master server (my.cnf)
# [mysqld]
# server-id = 1
# log_bin = mysql-bin
# binlog_format = ROW
# 
# -- On slave server (my.cnf)
# [mysqld]
# server-id = 2
# relay-log = slave-relay-bin
# log_bin = mysql-bin
# 
# -- On slave server (SQL commands)
# CHANGE MASTER TO
#   MASTER_HOST='master.example.com',
#   MASTER_USER='replicator',
#   MASTER_PASSWORD='strongpassword',
#   MASTER_LOG_FILE='mysql-bin.000001',
#   MASTER_LOG_POS=0;
# 
# START SLAVE;TER_HOST='master.example.com',
  MASTER_USER='replicator',
  MASTER_PASSWORD='strongpassword# NOTE: The following code had syntax errors and was commented out
# 
# ### Sharding
# 
# Sharding distributes data across multiple database instances based on a shard key.
# 
# **Sharding Strategies:**
# - **Range-Based**: # NOTE: The following code had syntax errors and was commented out
# # // Configure shard servers
# # sh.addShard("shard01/shard01server01:27017,shard01server02:27017,shard01server03:27017")
# # sh.addShard("shard02/shard02server01:27017,shard02server02:27017,shard02server03:27017")
# # 
# # // Enable sharding for a database
# # sh.enableSharding("mydatabase")
# # 
# # // Shard a collection using a key
# # sh.shardCollection("mydataba# NOTE: The following code had syntax errors and was commented out
# # -- Create distributed table
# # SELECT create_distributed_table('users', 'user_id');
# # 
# # -- Insert data (automatically sharded)
# # INSERT INTO users (user_id, name, email) VALUES (1, 'John', 'john@example.com');database")
# 
# // Shard a collection using a key
# sh.shardCol# NOTE: The following code had syntax errors and was commented out
# # -- Original wide table
# # CREATE TABLE user_profiles (
# #   user_id INT PRIMARY KEY,
# #   username VARCHAR(50),
# #   email VARCHAR(100),
# #   password_hash VARCHAR(256),
# #   biography TEXT,
# #   profile_image BYTEA,
# #   preferences JSON,
# #   last_login TIMESTAMP
# # );
# # 
# # -- Vertically partitioned tables
# # CREATE TABLE user_core (
# #   user_id INT PRIMARY KEY,
# #   username VARCHAR(50),
# #   email VARCHAR(100),
# #   password_hash VARCHAR(256)
# # );
# # 
# # CREATE TABLE user_extended (
# #   user_id INT PRIMARY KEY,
# #   biography TEXT,
# #   profile_image BYTEA,
# #   FOREIGN KEY (user_id) REFERENCES user_core(user_id)
# # );
# # 
# # CREATE TABLE user_activity (
# #   user_id INT PRIMARY KEY,
# #   preferences JSON,
# #   last_login TIMESTAMP,
# #   FOREIGN KEY (user_id) REFERENCES user_core(user_id)
# # );E TABLE user_core (
#   user_id INT PRIMARY KEY,
#   username VARCHAR(50),
#   email VARCHAR(100),
#   password_hash VARCHAR(256)
# );
# 
# CREATE TABLE user_extended (
#   user_id INT PRIMARY KEY,
#   biography TEXT,
#   profile_image BYTEA,
#   FOREIGN KEY (user_id) REFERENCES user_core(user_id)
# );
# 
# CREATE TABLE user_activity (
#   user_id INT PRIMARY KEY,
#   preferences JSON,
#   last_login TIMESTAMP,
#   FOREIGN KEY (user_id) REFERENCES user_core(user_id)
# ); last_login TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES user_core(user_id)
);
```text

## CAP Theorem

The CAP theorem states that a distributed database system can only provide two of the following three guarantees simultaneously:

- **Consistency**: Every read receives the most recent write
- **Availability**: Every request receives a response (success or failure)
- **Partition Tolerance**: System continues operating despite network partitions

**Database Classification by CAP Properties:**

- **CA (Consistency + Availability)**
  - Traditional RDBMS (PostgreSQL, MySQL, SQL Server)
  - Note: These become CP when used in distributed configurations

- **CP (Consistency + Partition Tolerance)**
  - MongoDB (with majority writes)
  - HBase
  - Redis Cluster

- **AP (Availability + Partition Tolerance)**
  - Cassandra
  - CouchDB
  - DynamoDB (with eventual consistency)

## Denormalization# NOTE: The following code had syntax errors and was commented out
# -- Normalized model
# CREATE TABLE orders (
#   order_id INT PRIMARY KEY,
#   user_id INT,
#   order_date TIMESTAMP,
#   FOREIGN KEY (user_id) REFERENCES users(id)
# );
# 
# CREATE TABLE order_items (
#   id INT PRIMARY KEY,
#   order_id INT,
#   product_id INT,
#   quantity INT,
#   price DECIMAL(10,2),
#   FOREIGN KEY (order_id) REFERENCES orders(order_id),
#   FOREIGN KEY (product_id) REFERENCES products(id)
# );
# 
# -- Denormalized model for reporting
# CREATE TABLE order_reports (
#   order_id INT,
#   user_id INT,
#   username VARCHAR(50),  -- Denormalized from users
#   email VARCHAR(100),    -- Denormalized from users
#   order_date TIMESTAMP,
#   product_id INT,
#   product_name VARCHAR(100),  -- Denormalized from products
#   quantity INT,
#   price DECIMAL(10,2),
#   total DECIMAL(10,2), # NOTE: The following code had syntax errors and was commented out
# # docker-compose.yml
# version: '3'
# 
# services:
#   postgres:
#     image: postgres:14
#     environment:
#       POSTGRES_USER: myuser
#       POSTGRES_PASSWORD: mypassword
#       POSTGRES_DB: mydb
#     ports:
#       - "5432:5432"
#     volumes:
#       - postgres-data:/var/lib/postgresql/data
#       - ./init-scripts:/docker-entrypoint-initdb.d
#     restart: always
# 
#   pgadmin:
#     image: dpage/pgadmin4
#     environment:
#       PGADMIN_DEFAULT_EMAIL: admin@example.com
#       PGADMIN_DEFAULT_PASSWORD: adminpassword
#     ports:
#       - "8080:80"
#  # NOTE: The following code had syntax errors and was commented out
# # docker-compose.yml
# version: '3'
# 
# services:
#   mongo1:
#     image: mongo:5
#     container_name: mongo1
#     command: mongod --replSet rs0 --bind_ip_all
#     ports:
#       - "27017:27017"
#     restart: always
#     volumes:
#       - mongo1-data:/data/db
#     networks:
#       - mongo-network
# 
#   mongo2:
#     image: mongo:5
#     container_name: mongo2
#     command: mongod --replSet rs0 --bind_ip_all
#     ports:
#       - "27018:27017"
#     restart: always
#     volumes:
#       - mongo2-data:/data/db
#     networks:
#       - mongo-network
# 
#   mongo3:
#     image: mongo:5
#     container_name: mongo3
#     command: mongod --replSet rs0 --bind_ip_all
#     ports:
#       - "27019:27017"
#     restart: always
#     volumes:
#       - mongo3-data:/data/db
#     networks:
#       - mongo-network
# 
#   # Initialize replica set
#   mongo-init:
#     image: mongo:5
#     depends_on:
#       - mongo1
#       - mongo2
#       - mongo3
#     networks:
#       - mongo-network
#     command: >
#       bash -c "
#         sleep 10 &&
#         mongo --host mongo1:27017 --eval '
#           rs.initiate({
#             _id: \"rs0\",
#             members: [
#               {_id: 0, host: \"mongo1:27017\"},
#               {_id: 1, host: \"mongo2:27017\"},
#               {_id: 2, host: \"mongo3# NOTE: The following code had syntax errors and was commented out
# # docker-compose.yml
# version: '3'
# 
# services:
#   redis:
#     image: redis:6
#     command: redis-server --appendonly yes --requirepass strongpassword
#     ports:
#       - "6379:6379"
#     volumes:
#       - redis-data:/data
#     restart: always
# 
# volumes:
#   redis-data:
      - mongo-network
    command: >
      bash -c "
        sleep 10 &&
        mongo --host mongo1:27017 --eval '
          rs.initiate({
            _id: \"rs0\",
            members: [
              {_id: 0, host: \"mongo1:27017\"},
              {_id: 1, host: \"mongo2:27017\"},
              {_id: 2, host: \"mongo3:27017\"}
            ]
          })
        '
      "

networks:
  mongo-network:

volumes:
  mongo1-data:
  mongo2-data:
  mongo3-data:
```

### Redis Cache with Persistence

```yaml
# docker-compose.yml
version: '3'

services:
  redis:
    image: redis:6
    command: redis-server --appendonly yes --requirepass strongpassword
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: always

volumes:
  redis-data:
```

## Best Practices

1. **Choose the Right Database**: Select based on data structure, query patterns, and scale requirements
2. **Plan for Scale**: Design with horizontal scaling in mind from the beginning
3. **Connection Pooling**: Use connection pools for efficient resource utilization
4. **Monitor Performance**: Implement comprehensive monitoring with alerts
5. **Regular Backups**: Automated backup strategy with testing restoration procedures
6. **Index Strategically**: Create indexes for frequent query patterns, but avoid over-indexing
7. **Query Optimization**: Regularly review and optimize slow queries
8. **Security**: Follow principle of least privilege, encrypt sensitive data, audit access
9. **High Availability**: Plan for failovers with proper replication strategy
10. **Consider Caching**: Implement appropriate caching strategy to reduce database load

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Redis Documentation](https://redis.io/documentation)
- [Database Scaling Patterns](https://www.citusdata.com/blog/2017/08/09/five-data-models-for-sharding/)
- [CAP Theorem](https://www.ibm.com/cloud/learn/cap-theorem)
