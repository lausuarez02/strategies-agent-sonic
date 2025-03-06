from web3 import Web3
import yaml
import os

# Load Config
with open("configs/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Initialize both networks
eth_web3 = Web3(Web3.HTTPProvider(config["networks"]["sonic"]["rpc_url"]))
arb_web3 = Web3(Web3.HTTPProvider(config["networks"]["arbitrum"]["rpc_url"]))

private_key = os.getenv("PRIVATE_KEY") or config["networks"]["arbitrum"]["private_key"]
sonic_account = eth_web3.eth.account.from_key(private_key)
arb_account = arb_web3.eth.account.from_key(private_key)

def borrow_and_farm():
    """Execute cross-chain borrowing & farming logic."""
    print("Borrowing on Arbitrum, farming on Sonic...")
    # Implement cross-chain logic here

if __name__ == "__main__":
    borrow_and_farm()
