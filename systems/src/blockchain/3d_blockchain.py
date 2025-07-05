"""
3D Blockchain Python Implementation
----------------------------------
Foundational code for a 3D blockchain system supporting fiat/crypto, DeFi, referral, tax, plug-and-play APIs, and web3 website-on-chain.
"""
import hashlib
import time
import json
from typing import List, Dict, Any

class Block:
    def __init__(self, x: int, y: int, z: int, transactions: List[Dict[str, Any]], previous_hash: str):
        self.x = x
        self.y = y
        self.z = z
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    def calculate_hash(self) -> str:
        block_string = json.dumps({
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    def mine_block(self, difficulty: int):
        while self.hash[:difficulty] != "0" * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()

class Blockchain3D:
    def __init__(self, difficulty: int = 4):
        self.chain: List[Block] = [self.create_genesis_block()]
        self.difficulty = difficulty
    def create_genesis_block(self) -> Block:
        return Block(0, 0, 0, [{"info": "Genesis Block"}], "0")
    def get_latest_block(self) -> Block:
        return self.chain[-1]
    def add_block(self, new_block: Block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True
    def create_block(self, x: int, y: int, z: int, transactions: List[Dict[str, Any]]):
        latest_block = self.get_latest_block()
        new_block = Block(x, y, z, transactions, latest_block.hash)
        self.add_block(new_block)

# Example Usage
if __name__ == "__main__":
    blockchain = Blockchain3D()
    blockchain.create_block(1, 2, 1, [{"from": "Alice", "to": "Bob", "amount": 10, "currency": "USD"}])
    blockchain.create_block(2, 2, 1, [{"from": "Bob", "to": "Charlie", "amount": 20, "currency": "BTC"}])
    print("Blockchain valid:", blockchain.is_chain_valid())
    for block in blockchain.chain:
        print(vars(block))
