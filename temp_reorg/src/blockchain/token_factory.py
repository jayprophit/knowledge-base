"""
User-Created Custom Token Framework for 3D Blockchain
-----------------------------------------------------
Implements:
- CustomToken: User-defined tokens (ERC-20 style)
- TokenFactory: Deploys/manages user tokens
- WebsiteTokenRegistry: Links tokens to websites/products
- TokenStaking: Stake/unstake user tokens

See documentation in docs/blockchain/token_factory.md
"""

class CustomToken:
    def __init__(self, name, symbol, initial_supply, decimals=18, owner_address=None):
        self.name = name
        self.symbol = symbol
        self.total_supply = initial_supply
        self.decimals = decimals
        self.owner_address = owner_address
        self.balances = {owner_address: initial_supply}
        self.allowances = {}

    def transfer(self, sender, recipient, amount):
        if self.balances.get(sender, 0) >= amount:
            self.balances[sender] -= amount
            self.balances[recipient] = self.balances.get(recipient, 0) + amount
            print(f"Transferred {amount} {self.symbol} from {sender} to {recipient}")
        else:
            print("Insufficient balance for the transfer.")

    def approve(self, owner, spender, amount):
        self.allowances[(owner, spender)] = amount
        print(f"{owner} approved {spender} to spend {amount} {self.symbol}")

    def transfer_from(self, spender, owner, recipient, amount):
        allowed = self.allowances.get((owner, spender), 0)
        if allowed >= amount and self.balances[owner] >= amount:
            self.balances[owner] -= amount
            self.balances[recipient] = self.balances.get(recipient, 0) + amount
            self.allowances[(owner, spender)] -= amount
            print(f"{spender} transferred {amount} {self.symbol} from {owner} to {recipient}")
        else:
            print("Insufficient allowance or balance for the transfer.")

class TokenFactory:
    def __init__(self):
        self.deployed_tokens = {}  # owner_address -> CustomToken
    def create_token(self, name, symbol, initial_supply, owner_address, decimals=18):
        new_token = CustomToken(name, symbol, initial_supply, decimals, owner_address)
        self.deployed_tokens[owner_address] = new_token
        print(f"Token {name} ({symbol}) created with a total supply of {initial_supply}.")
        return new_token
    def get_token(self, owner_address):
        return self.deployed_tokens.get(owner_address, None)

class WebsiteTokenRegistry:
    def __init__(self):
        self.website_tokens = {}  # website_address -> CustomToken
    def register_website_token(self, website_address, token_contract):
        self.website_tokens[website_address] = token_contract
        print(f"Token {token_contract.name} ({token_contract.symbol}) linked to website {website_address}")
    def get_website_token(self, website_address):
        return self.website_tokens.get(website_address)

class TokenStaking:
    def __init__(self):
        self.staked_balances = {}  # user_address -> staked amount
    def stake_tokens(self, user_address, token_contract, amount):
        if token_contract.balances.get(user_address, 0) >= amount:
            token_contract.balances[user_address] -= amount
            self.staked_balances[user_address] = self.staked_balances.get(user_address, 0) + amount
            print(f"{user_address} staked {amount} {token_contract.symbol}")
        else:
            print("Insufficient balance to stake.")
    def unstake_tokens(self, user_address, token_contract, amount):
        if self.staked_balances.get(user_address, 0) >= amount:
            token_contract.balances[user_address] += amount
            self.staked_balances[user_address] -= amount
            print(f"{user_address} unstaked {amount} {token_contract.symbol}")
        else:
            print("Insufficient staked tokens to unstake.")

# Example usage for documentation is provided in docs/blockchain/token_factory.md
