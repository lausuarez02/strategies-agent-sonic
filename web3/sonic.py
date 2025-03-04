import yaml
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

# Load Config
with open("configs/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Connect to Web3
web3 = Web3(Web3.HTTPProvider(config["network"]["rpc_url"]))
private_key = os.getenv("PRIVATE_KEY") or config["network"]["private_key"]
account = web3.eth.account.from_key(private_key)

# Sonic Farm Contract ABI (Minimal Example)
SONIC_FARM_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "getPendingRewards",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
]

# Contract Instance
sonic_farm = web3.eth.contract(
    address=config["contracts"]["sonic_farm"], abi=SONIC_FARM_ABI
)

def get_rewards():
    """Fetch pending rewards from SonicFarm."""
    rewards = sonic_farm.functions.getPendingRewards().call()
    return web3.from_wei(rewards, "ether")

if __name__ == "__main__":
    print(f"Pending Rewards: {get_rewards()} ETH")
