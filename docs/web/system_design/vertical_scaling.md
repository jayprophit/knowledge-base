---
id: web-system-design-vertical-scaling
title: Vertical Scaling in System Design
description: Documentation on vertical scaling, its trade-offs, and implementation strategies
author: Knowledge Base System
created_at: 2025-07-02
updated_at: 2025-07-02
version: 1.0.0
tags:
  - vertical_scaling
  - scalability
  - system_design
relationships:
  prerequisites: []
  successors: []
  related:
    - sharding.md
    - replication.md
    - database_overview.md
---

# Vertical Scaling in System Design

## Overview

Vertical scaling (scaling up) means adding more resources (CPU, RAM, storage) to a single server to improve performance. It is often the first step in scaling a system but has practical and economic limits.

## Advantages
- Simple to implement
- No application changes required
- Useful for monolithic systems

## Disadvantages
- Hardware limits
- Single point of failure
- Downtime required for upgrades
- Cost increases rapidly with scale

## Example: Upgrading a Database Server
- Add more RAM/CPU to the existing database server
- Move to a more powerful cloud instance (e.g., AWS EC2)

## When to Use
- Small to medium workloads
- Applications not designed for distributed scaling

## Best Practices
- Monitor resource utilization
- Plan for horizontal scaling as growth continues
- Use cloud providers for flexible scaling

## Related Topics
- [Sharding](sharding.md)
- [Replication](replication.md)
- [Database Overview](../databases/database_overview.md)

## References
- [AWS Vertical Scaling](https://aws.amazon.com/blogs/database/vertical-and-horizontal-scaling/)
