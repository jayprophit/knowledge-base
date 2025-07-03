# Layer-2, DeFi, Cross-Chain, and Referral Enhancements

## Overview

This document describes the advanced blockchain features added to the 3D and website-as-blockchain systems, including:
- **Layer-2 fast/cheap transactions** (state channels, rollups)
- **Dynamic transaction fees**
- **On-chain swaps via liquidity pools (AMM)**
- **Cross-chain bridges (HTLC)**
- **Referral system**

These features enable the blockchain to support fast, low-cost transactions, on-chain swaps/conversions, cross-chain asset transfers, and user/community incentives.

See also: [`src/blockchain/layer2_and_defi.py`](../../src/blockchain/layer2_and_defi.py)

## Features

### Layer-2 Transactions & Rollups
- Use state channels and rollups to batch transactions off-chain, reducing fees and increasing speed.
- Rollups allow batching of many user interactions (comments, likes, data exchanges) and submitting them on-chain as a single transaction.

### Dynamic Transaction Fees
- Transaction fees are adjusted dynamically based on network congestion.
- Layer-2 transactions have minimal or zero fees.

### On-Chain Swaps & Liquidity Pools
- Users can swap cryptocurrencies directly on-chain using automated market makers (AMMs).
- Liquidity pools allow users to provide liquidity and earn fees from swaps.

### Cross-Chain Bridges & HTLC
- Cross-chain bridges enable asset swaps between different blockchains (e.g., BTC <-> ETH).
- Hashed Timelock Contracts (HTLC) ensure atomic, trustless swaps across chains.

### Referral System
- Users can refer others and earn rewards for interactions by referees.
- Incentives for both referrer and referee.

## Example Python Implementation

See [`src/blockchain/layer2_and_defi.py`](../../src/blockchain/layer2_and_defi.py) for class implementations:
- `Transaction` (Layer-2, dynamic fees)
- `Rollup` (batching)
- `LiquidityPool` (AMM swaps)
- `CrossChainBridge` (cross-chain swaps)
- `HTLC` (atomic cross-chain swaps)
- `ReferralSystem` (referral rewards)

## Example Usage

```python
# Layer-2 fast transaction
tx = Transaction("user_1", "user_2", 100, currency="ETH", layer_2=True)
tx.execute_transaction()

# Rollup batching
rollup = Rollup()
rollup.add_transaction(tx)
rollup.submit_batch()

# Liquidity pool swap
lp = LiquidityPool()
lp.add_liquidity("ETH_BTC", 100, 50)
lp.swap("ETH_BTC", "token_a", 10)

# Cross-chain bridge
bridge = CrossChainBridge()
bridge.add_bridge("BTC", "btc_to_eth_bridge_contract")
bridge.add_bridge("ETH", "eth_to_btc_bridge_contract")
bridge.convert("user_1", "BTC", "ETH", 0.1)

# HTLC atomic swap
htlc = HTLC()
secret = "mysecret123"
secret_hash = hashlib.sha256(secret.encode()).hexdigest()
htlc.create_htlc("user_1", "user_2", 0.5, secret_hash, expiry_time=3600)
htlc.redeem_htlc(secret, secret_hash)

# Referral rewards
ref_sys = ReferralSystem()
ref_sys.add_referral("user_1", "user_5")
ref_sys.reward_referral("user_5", 100)
```

## Integration & References
- Integrated with [`website_blockchain.py`](../../src/blockchain/website_blockchain.py) and [`3d_blockchain.py`](../../src/blockchain/3d_blockchain.py)
- [Layer 2 Scaling](https://ethereum.org/en/developers/docs/scaling/layer-2-rollups/)
- [Automated Market Maker](https://uniswap.org/whitepaper.pdf)
- [Hashed Timelock Contracts](https://en.bitcoin.it/wiki/Hashed_Timelock_Contract)
- [DeFi Concepts](https://defipulse.com/)
