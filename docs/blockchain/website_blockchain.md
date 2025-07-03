# Website-as-Blockchain System Documentation

## Overview

This document describes the architecture and usage of the Website-as-Blockchain system, where each website is represented as a unique blockchain address and each page or interaction is a block. The system is Web2/Web3 compatible, supports decentralized storage, inter-website communication, and rewards users for interactions using PoS, DPoS, and DPoF consensus models.

## Features

- **Website as Blockchain:** Each website is a unique chain; the homepage is the genesis block, and each subpage or user interaction (like, comment, share, upload, buy, sell, etc.) is a block in the chain.
- **Page Data & Metadata:** Stores HTML, CSS, JS, or IPFS hash in each block, along with metadata (author, SEO, etc.).
- **Web2/Web3 Compatibility:** REST API for traditional access, smart contract integration for Web3.
- **Decentralized Storage:** Option to store page content in IPFS/Filecoin, with only hashes stored on-chain.
- **Inter-Website Communication:** Links and references between websites can be tracked and verified via blockchain.
- **Reward System:** Users earn coins/tokens for interactions (comments, likes, shares, uploads, buys, sells, transfers, etc.).
- **Consensus Models:** Supports Proof of Stake (PoS), Delegated Proof of Stake (DPoS), and Delegated Proof of Ownership (DPoF).

## Reward System & Consensus

- **Interactions:** Each user action (like, comment, share, upload, transaction) creates a block and may earn rewards.
- **PoS:** Users can stake coins to validate interactions and earn additional rewards.
- **DPoS:** Users elect delegates who validate blocks; both delegates and voters earn rewards.
- **DPoF:** Content creators earn extra rewards when their content is interacted with.

### Example Reward Table

| Interaction Type | Base Reward | PoS Bonus (if staked) | DPoS Delegate Bonus | DPoF Ownership Bonus |
|------------------|-------------|----------------------|---------------------|---------------------|
| Like             | 1           | +5% of stake         | +10% to delegate    | +20% for creator    |
| Comment          | 2           | +5% of stake         | +10% to delegate    | +20% for creator    |
| Share            | 5           | +5% of stake         | +10% to delegate    | +20% for creator    |
| Video Upload     | 10          | +5% of stake         | +10% to delegate    | +20% for creator    |
| Image Upload     | 3           | +5% of stake         | +10% to delegate    | +20% for creator    |
| Transaction      | 1% of stake | +5% of stake         | +10% to delegate    | +20% for creator    |


## Example Python Implementation

See [`src/blockchain/website_blockchain.py`](../../src/blockchain/website_blockchain.py) for the full code, including:

- Block and WebsiteBlockchain classes
- Methods for adding interactions, managing delegates, voting, and calculating rewards
- Example usage demonstrating user interactions, staking, delegate voting, and reward balances

```python
# Example: Adding an interaction with staking and delegate voting
website = WebsiteBlockchain("example.com")
website.add_webpage_block("Blog", "<html>...</html>", "share", "user_1", stake=50)
website.add_delegate("user_3")
website.vote_delegate("user_1", "user_3")
```

## API Example

A REST API can expose website pages and user balances. Example endpoints:

```http
GET /website/<page_name>
GET /user/<user_address>/balance
```

Returns the content/metadata for a page or the current balance for a user.

## Future Enhancements

- ENS integration for decentralized DNS
- Smart contract-powered dynamic content
- DeFi/token-gated access to pages
- 3D visualization of website chains and user interactions
- Referral and pyramid rewards via smart contracts

## References

- [IPFS](https://ipfs.tech/)
- [ENS](https://ens.domains/)
- [Web3 Concepts](https://ethereum.org/en/web3/)
- [Proof of Stake (PoS)](https://ethereum.org/en/developers/docs/consensus-mechanisms/pos/)
- [Delegated Proof of Stake (DPoS)](https://www.investopedia.com/terms/d/delegated-proof-stake-dpos.asp)
- [Delegated Proof of Ownership (DPoF)](https://blockchainhub.net/blog/delegated-proof-of-ownership/)
