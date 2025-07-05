"""
Layer-2, DeFi, Cross-Chain, and Referral Enhancements for 3D Blockchain
----------------------------------------------------------------------
Implements:
- Layer-2 fast/cheap transactions (state channels, rollups)
- Dynamic transaction fees
- On-chain swaps via liquidity pools (AMM)
- Cross-chain bridges (HTLC)
- Referral system

See documentation in docs/blockchain/3d_blockchain.md and website_blockchain.md
"""
import hashlib
import time
from collections import defaultdict
from typing import List, Dict, Any

class Transaction:
    def __init__(self, sender, receiver, amount, currency="native", gas_fee=0.001, layer_2=False):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.currency = currency  # Native or other tokens
        self.timestamp = time.time()
        self.gas_fee = gas_fee if not layer_2 else 0  # Layer-2 has no/low fees
        self.layer_2 = layer_2
        self.status = "pending"

    def execute_transaction(self):
        if self.layer_2:
            print(f"Layer-2 transaction: {self.sender} -> {self.receiver} ({self.amount} {self.currency})")
        else:
            print(f"On-chain transaction: {self.sender} -> {self.receiver} ({self.amount} {self.currency})")
        self.status = "completed"

class Rollup:
    def __init__(self):
        self.pending_transactions = []
    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)
        print(f"Transaction added to rollup: {transaction.sender} -> {transaction.receiver} ({transaction.amount})")
    def submit_batch(self):
        if not self.pending_transactions:
            print("No transactions to submit in the rollup.")
            return
        print(f"Submitting {len(self.pending_transactions)} transactions as a single rollup on-chain...")
        self.pending_transactions = []

class LiquidityPool:
    def __init__(self):
        self.pools = defaultdict(lambda: {"token_a": 0, "token_b": 0})
    def add_liquidity(self, pool_name, token_a_amount, token_b_amount):
        self.pools[pool_name]["token_a"] += token_a_amount
        self.pools[pool_name]["token_b"] += token_b_amount
        print(f"Liquidity added to {pool_name}: {token_a_amount} Token A, {token_b_amount} Token B")
    def swap(self, pool_name, input_token, input_amount):
        pool = self.pools[pool_name]
        if input_token == "token_a":
            output_amount = (input_amount * pool["token_b"]) / (pool["token_a"] + input_amount)
            pool["token_a"] += input_amount
            pool["token_b"] -= output_amount
            print(f"Swapped {input_amount} Token A for {output_amount} Token B")
        else:
            output_amount = (input_amount * pool["token_a"]) / (pool["token_b"] + input_amount)
            pool["token_b"] += input_amount
            pool["token_a"] -= output_amount
            print(f"Swapped {input_amount} Token B for {output_amount} Token A")
        return output_amount

class CrossChainBridge:
    def __init__(self):
        self.bridge_contracts = {}
    def add_bridge(self, token_name, bridge_address):
        self.bridge_contracts[token_name] = bridge_address
        print(f"Bridge added for {token_name} at {bridge_address}")
    def convert(self, user_address, from_token, to_token, amount):
        if from_token in self.bridge_contracts and to_token in self.bridge_contracts:
            print(f"Converting {amount} {from_token} to {to_token} for {user_address}")
            converted_amount = amount * 0.95
            return converted_amount
        else:
            print("Bridge not available for the requested tokens.")
            return None

class HTLC:
    def __init__(self):
        self.locked_contracts = {}
    def create_htlc(self, user_address, recipient_address, amount, secret_hash, expiry_time):
        self.locked_contracts[secret_hash] = {
            "user": user_address,
            "recipient": recipient_address,
            "amount": amount,
            "expiry": time.time() + expiry_time,
            "redeemed": False
        }
        print(f"HTLC created: {amount} locked for {recipient_address} by {user_address}")
    def redeem_htlc(self, secret, secret_hash):
        if secret_hash in self.locked_contracts:
            contract = self.locked_contracts[secret_hash]
            if time.time() < contract["expiry"] and not contract["redeemed"]:
                if hashlib.sha256(secret.encode()).hexdigest() == secret_hash:
                    contract["redeemed"] = True
                    print(f"HTLC redeemed: {contract['amount']} sent to {contract['recipient']}")
                    return True
                else:
                    print("Invalid secret provided.")
            else:
                print("HTLC expired or already redeemed.")
        return False

class ReferralSystem:
    def __init__(self):
        self.referrals = {}
        self.referral_rewards = 0.01
    def add_referral(self, referrer, referee):
        self.referrals[referee] = referrer
        print(f"Referral registered: {referrer} referred {referee}")
    def reward_referral(self, referee, transaction_amount):
        referrer = self.referrals.get(referee)
        if referrer:
            referrer_reward = transaction_amount * self.referral_rewards
            referee_reward = referrer_reward / 2
            print(f"{referrer} earned {referrer_reward} for referring {referee}")
            print(f"{referee} earned {referee_reward} for being referred.")
            return referrer_reward, referee_reward
        return 0, 0

# Example usage for each feature is included in the documentation.
