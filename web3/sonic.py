import yaml
from web3 import Web3
import os
from dotenv import load_dotenv
from abis.sonic import SONIC_VAULT_ABI, SONIC_ORACLE_ABI, SONIC_ZAPPER_ABI
from abis.debridge import DEBRIDGE_ABI

load_dotenv()

# Load Config
with open("configs/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Get RPC URLs with API keys
sonic_rpc = Web3(Web3.HTTPProvider(config["networks"]["sonic"]["rpc_url"]))
arb_rpc = config["networks"]["arbitrum"]["rpc_url"].replace("${ARB_RPC_KEY}", os.getenv("ARB_RPC_KEY"))

# Initialize Web3 with the complete URLs
sonic_web3 = Web3(Web3.HTTPProvider(sonic_rpc))
arb_web3 = Web3(Web3.HTTPProvider(arb_rpc))

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

# Sonic Oracle Contract ABI (Minimal Example)
SONIC_ORACLE_ABI = [
    {
        "inputs": [{"type": "string"}],
        "name": "price",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
]

# Contract instances for Ethereum
eth_sonic_vault = sonic_web3.eth.contract(
    address=config["contracts"]["sonic"]["sonic_vault"],
    abi=SONIC_VAULT_ABI
)

eth_sonic_oracle = sonic_web3.eth.contract(
    address=config["contracts"]["sonic"]["sonic_oracle"],
    abi=SONIC_ORACLE_ABI
)

# Contract instance for Arbitrum
arb_debridge = arb_web3.eth.contract(
    address=config["contracts"]["arbitrum"]["debridge_gate"],
    abi=DEBRIDGE_ABI
)

def get_rewards():
    """Fetch pending rewards from SonicFarm."""
    rewards = sonic_farm.functions.getPendingRewards().call()
    return web3.from_wei(rewards, "ether")

def estimate_gas_cost(web3, transaction):
    """Updated to take web3 instance as parameter"""
    try:
        # Get gas estimate
        gas_estimate = web3.eth.estimate_gas(transaction)
        
        # Get current gas price
        gas_price = web3.eth.gas_price
        
        # Calculate cost in ETH
        cost_in_wei = gas_estimate * gas_price
        cost_in_eth = web3.from_wei(cost_in_wei, 'ether')
        
        # Get ETH price from Oracle
        eth_price = eth_sonic_oracle.functions.getAssetPrice("ETH").call()
        cost_in_usd = cost_in_eth * web3.from_wei(eth_price, 'ether')
        
        return {
            'gas_units': gas_estimate,
            'gas_price_gwei': web3.from_wei(gas_price, 'gwei'),
            'cost_eth': cost_in_eth,
            'cost_usd': cost_in_usd
        }
    except Exception as e:
        print(f"Error estimating gas: {e}")
        return None

# Example usage:
def example_transaction_estimate():
    # Example: Estimate gas for a deposit
    transaction = sonic_vault.functions.deposit(
        amount=web3.to_wei(1, 'ether')
    ).build_transaction({
        'from': account.address,
        'nonce': web3.eth.get_transaction_count(account.address),
        'gas': 2000000,  # Max gas, will be estimated
        'gasPrice': web3.eth.gas_price
    })
    
    gas_estimate = estimate_gas_cost(web3, transaction)
    if gas_estimate:
        print(f"Estimated gas units: {gas_estimate['gas_units']}")
        print(f"Gas price (Gwei): {gas_estimate['gas_price_gwei']}")
        print(f"Estimated cost in ETH: {gas_estimate['cost_eth']:.6f}")
        print(f"Estimated cost in USD: ${gas_estimate['cost_usd']:.2f}")

if __name__ == "__main__":
    example_transaction_estimate()
