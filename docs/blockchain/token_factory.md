---
author: Knowledge Base Automation System
created_at: '2025-07-04'
description: Documentation on Token Factory for blockchain/token_factory.md
title: Token Factory
updated_at: '2025-07-04'
version: 1.0.0
---

# User-Created Token Framework for 3D Blockchain

## Overview

This document describes the system for allowing users to create, manage, and integrate their own tokens (like ERC-20) within the 3D blockchain platform. These tokens can be linked to websites or products and participate in staking, swaps, and liquidity pools.

See also: [`src/blockchain/token_factory.py`](../../src/blockchain/token_factory.py)

## Features

- **Custom Token Creation**: Users can define name, symbol, supply, decimals, and ownership.
- **Token Management**: Transfer, approve, and transfer-from operations supported.
- **Token Factory**: Deploy and manage user tokens with customizable parameters.
- **Website/Product Integration**: Link tokens to websites or products for use in rewards, payments, and interactions.
- **Staking**: Stake/unstake custom tokens for rewards or governance.

## Example Python Implementation

See [`src/blockchain/token_factory.py`](../../src/blockchain/token_factory.py) for class implementations:
- `CustomToken`: User-defined token contract (ERC-20 style)
- `TokenFactory`: Deploys and manages user tokens
- `WebsiteTokenRegistry`: Links tokens to websites/products
- `TokenStaking`: Stake/unstake user tokens

## Example Usage

```python
# User A creates a token for their website
user_a_token = CustomToken("WebsiteCoin", "WSC", initial_supply = 1000000, owner_address="user_a_address")

# User B creates a token for their product
token_factory = TokenFactory()
user_b_token = token_factory.create_token("ProductCoin", "PC", 500000, owner_address="user_b_address")

# Transfer and approve tokens
user_a_token.transfer("user_a_address", "user_b_address", 500)
user_a_token.approve("user_a_address", "user_c_address", 200)
user_a_token.transfer_from("user_c_address", "user_a_address", "user_d_address", 150)

# Link tokens to websites / products
website_registry = WebsiteTokenRegistry()
website_registry.register_website_token("website_123.com", user_a_token)
website_registry.register_website_token("product_456", user_b_token)

# Stake tokens
staking = TokenStaking()
staking.stake_tokens("user_a_address", user_a_token, 1000):
```