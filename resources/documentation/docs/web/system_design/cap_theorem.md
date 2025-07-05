---
id: web-system-design-cap-theorem
title: CAP Theorem in System Design
description: Documentation on the CAP theorem, its implications, and real-world examples
author: Knowledge Base System
created_at: 2025-07-02
updated_at: 2025-07-02
version: 1.0.0
tags:
- cap_theorem
- databases
- system_design
relationships:
  prerequisites: []
  successors: []
  related:
  - database_overview.md
  - sharding.md
  - replication.md
---

# CAP Theorem in System Design

## Overview

The CAP theorem states that a distributed system can only guarantee two out of three properties: Consistency, Availability, and Partition Tolerance.

## Properties
- **Consistency:** Every read receives the most recent write
- **Availability:** Every request receives a (non-error) response
- **Partition Tolerance:** System continues to operate despite network partitions

## Real-World Examples
- **CP (Consistency + Partition Tolerance):** HBase, MongoDB (with write concern)
- **AP (Availability + Partition Tolerance):** Couchbase, DynamoDB
- **CA (Consistency + Availability):** Single-node relational databases

## Implications
- Trade-offs are inevitable in distributed systems
- Choose based on application requirements

## Best Practices
- Understand your application's needs
- Design for graceful degradation
- Monitor for network partitions

## Related Topics
- [Database Overview](../databases/database_overview.md)
- [Sharding](sharding.md)
- [Replication](replication.md)

## References
- [CAP Theorem](https://en.wikipedia.org/wiki/CAP_theorem)
- [Brewer's CAP Theorem](https://www.infoq.com/articles/cap-twelve-years-later/)
