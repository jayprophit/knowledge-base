"""
Website-as-Blockchain Python Implementation (with Rewards & Consensus)
---------------------------------------------------------------------
Each website is its own blockchain address; each page or interaction is a block. Supports Web2/Web3 compatibility, decentralized storage, inter-website communication, and user rewards for interactions (comments, likes, shares, uploads, buys, sells, etc.). Implements PoS, DPoS, and DPoF consensus models.
"""
import hashlib
import time
import json
from collections import defaultdict
from typing import List, Dict, Any

class Block:
    def __init__(self, page_name: str, content: str, previous_hash: str, page_metadata: Dict[str, Any],
                 interaction_type: str, user_address: str, miner_address: str, stake: float = 0.0):
        self.page_name = page_name
        self.timestamp = time.time()
        self.content = content  # HTML/CSS/JS or IPFS hash
        self.page_metadata = page_metadata
        self.previous_hash = previous_hash
        self.nonce = 0
        self.interaction_type = interaction_type  # e.g., like, comment, share, upload, buy, sell, etc.
        self.user_address = user_address  # Address of the user making the interaction
        self.miner_address = miner_address  # Address of the miner who mines the block
        self.stake = stake  # Coins staked (PoS, DPoS)
        self.rewards = 0  # Rewards for the interaction
        self.hash = self.calculate_hash()
    def calculate_hash(self) -> str:
        block_string = json.dumps({
            'page_name': self.page_name,
            'timestamp': self.timestamp,
            'content': self.content,
            'page_metadata': self.page_metadata,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'interaction_type': self.interaction_type,
            'user_address': self.user_address,
            'miner_address': self.miner_address,
            'stake': self.stake
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    def mine_block(self, difficulty: int):
        while self.hash[:difficulty] != "0" * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()

class WebsiteBlockchain:
    def __init__(self, website_name: str, difficulty: int = 4, miner_reward: float = 50, transaction_fee: float = 0.01):
        self.website_name = website_name
        self.chain: List[Block] = [self.create_home_page_block()]
        self.difficulty = difficulty
        self.miner_reward = miner_reward  # Reward for miners for mining a block
        self.transaction_fee = transaction_fee  # Fee for each interaction/transaction (as a fraction of reward)
        self.users = defaultdict(float)  # User balances (rewards)
        self.miners = defaultdict(float)  # Miner balances (mining rewards)
        self.delegates = []  # DPoS delegates
        self.stakes = defaultdict(float)  # User stakes for PoS
        self.votes = defaultdict(list)  # Users voting for DPoS delegates
    def create_home_page_block(self) -> Block:
        # Genesis block for the website, representing the homepage
        return Block("Homepage", "<html><body>Welcome to the homepage</body></html>", "0", {}, "view", "system", "system")
    def get_latest_block(self) -> Block:
        return self.chain[-1]
    def add_delegate(self, user_address: str):
        """Add a user as a DPoS delegate."""
        if user_address not in self.delegates:
            self.delegates.append(user_address)
    def vote_delegate(self, voter: str, delegate: str):
        """Allow a user to vote for a delegate."""
        if delegate in self.delegates and voter not in self.votes[delegate]:
            self.votes[delegate].append(voter)
    def add_webpage_block(self, page_name: str, content: str, interaction_type: str, user_address: str, miner_address: str,
                          metadata: Dict[str, Any] = {}, stake: float = 0.0):
        """Add a new block representing an interaction on the webpage."""
        latest_block = self.get_latest_block()
        new_block = Block(page_name, content, latest_block.hash, metadata, interaction_type, user_address, miner_address, stake)
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        self.calculate_rewards(new_block)
    def calculate_rewards(self, block: Block):
        """
        Calculate rewards based on the type of interaction and consensus model.
        """
        reward = 0
        # Base rewards for interaction types
        if block.interaction_type == 'like':
            reward = 1
        elif block.interaction_type == 'comment':
            reward = 2
        elif block.interaction_type == 'share':
            reward = 5
        elif block.interaction_type == 'video':
            reward = 10
        elif block.interaction_type == 'image':
            reward = 3
        elif block.interaction_type == 'transaction':  # For buys, sells, transfers
            reward = block.stake * 0.01  # 1% of staked amount
        # Proof of Stake (PoS) rewards
        if block.stake > 0:
            staker_reward = block.stake * 0.05  # 5% of staked amount
            reward += staker_reward
            self.stakes[block.user_address] += block.stake
        # Delegated Proof of Stake (DPoS) rewards
        if block.user_address in self.delegates:
            delegate_reward = reward * 0.1  # 10% bonus for delegates
            reward += delegate_reward
            # Distribute a portion to voters
            voter_share = delegate_reward * 0.5 / len(self.votes[block.user_address]) if self.votes[block.user_address] else 0
            for voter in self.votes[block.user_address]:
                self.users[voter] += voter_share
        # Delegated Proof of Ownership (DPoF) rewards
        if block.interaction_type in ['video', 'image', 'content_upload']:
            ownership_reward = reward * 0.2  # 20% bonus for content creators
            reward += ownership_reward
        # Add rewards to the user's balance
        self.users[block.user_address] += reward
        block.rewards = reward
    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True
    def get_user_balance(self, user_address: str) -> float:
        """Return the current balance for a user."""
        return self.users[user_address]
    def get_miner_balance(self, miner_address: str) -> float:
        """Return the current balance for a miner."""
        return self.miners[miner_address]
    def get_delegate_votes(self, delegate_address: str) -> int:
        """Return the number of votes for a delegate."""
        return len(self.votes[delegate_address])

# Example Usage:
if __name__ == "__main__":
    # Initialize website blockchain
    website = WebsiteBlockchain("example.com")
    # Add users and miners interactions
    website.add_webpage_block("About Us", "<html><body>About Us Page</body></html>", "like", "user_1", "miner_1")
    website.add_webpage_block("Contact", "<html><body>Contact Us Page</body></html>", "comment", "user_2", "miner_1")
    website.add_webpage_block("Blog", "<html><body>New Blog Post</body></html>", "share", "user_1", "miner_2", stake=50)
    website.add_webpage_block("Gallery", "<html><body>Image Gallery</body></html>", "image", "user_3", "miner_2")
    # Proof of Stake interactions
    website.add_webpage_block("Market", "<html><body>Buy Now</body></html>", "transaction", "user_4", "miner_3", stake=100)
    # Add a delegate and vote for them in the DPoS system
    website.add_delegate("user_3")
    website.vote_delegate("user_1", "user_3")
    website.vote_delegate("user_2", "user_3")
    # Check user balances (rewards)
    print(f"User 1 balance: {website.get_user_balance('user_1')}")
    print(f"User 2 balance: {website.get_user_balance('user_2')}")
    print(f"User 3 balance (Delegate): {website.get_user_balance('user_3')}")
    print(f"User 4 balance: {website.get_user_balance('user_4')}")
    # Check miner balances (rewards from mining)
    print(f"Miner 1 balance: {website.get_miner_balance('miner_1')}")
    print(f"Miner 2 balance: {website.get_miner_balance('miner_2')}")
    print(f"Miner 3 balance: {website.get_miner_balance('miner_3')}")
    # Check votes for delegate
    print(f"Votes for User 3 (Delegate): {website.get_delegate_votes('user_3')}")
