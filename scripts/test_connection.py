from web3 import Web3
import yaml
from dotenv import load_dotenv
import os

load_dotenv()

def test_connections():
    # Load config
    with open("configs/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Test Sonic connection
    sonic_rpc = config["networks"]["sonic"]["rpc_url"]
    sonic_web3 = Web3(Web3.HTTPProvider(sonic_rpc))
    print(f"Sonic Connected: {sonic_web3.is_connected()}")
    if sonic_web3.is_connected():
        print(f"Sonic Chain ID: {sonic_web3.eth.chain_id}")
    
    # Test Arbitrum connection
    arb_rpc = config["networks"]["arbitrum"]["rpc_url"].replace("${ARB_RPC_KEY}", os.getenv("ARB_RPC_KEY"))
    arb_web3 = Web3(Web3.HTTPProvider(arb_rpc))
    print(f"Arbitrum Connected: {arb_web3.is_connected()}")
    if arb_web3.is_connected():
        print(f"Arbitrum Chain ID: {arb_web3.eth.chain_id}")

if __name__ == "__main__":
    test_connections() 