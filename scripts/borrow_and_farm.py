from web3 import Web3
import yaml
import os

# Load Config
with open("configs/config.yaml", "r") as f:
    config = yaml.safe_load(f)

web3 = Web3(Web3.HTTPProvider(config["network"]["rpc_url"]))
private_key = os.getenv("PRIVATE_KEY") or config["network"]["private_key"]
account = web3.eth.account.from_key(private_key)

def borrow_and_farm():
    """Execute cross-chain borrowing & farming logic."""
    print("Borrowing on chain A, farming on chain B...")
    # Interact with deBridge & Sonic contracts here

if __name__ == "__main__":
    borrow_and_farm()
