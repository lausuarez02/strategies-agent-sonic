from web3 import Web3
import yaml
import os

# Load Config
with open("configs/config.yaml", "r") as f:
    config = yaml.safe_load(f)

web3 = Web3(Web3.HTTPProvider(config["networks"]["sonic"]["rpc_url"]))
private_key = os.getenv("PRIVATE_KEY") or config["networks"]["sonic"]["private_key"]
account = web3.eth.account.from_key(private_key)

def auto_compound():
    """Trigger auto-compounding transaction."""
    tx = {
        "from": account.address,
        "to": config["contracts"]["sonic"]["sonic_vault"],
        "data": "0x",  # Replace with actual function call
        "gas": 200000,
        "gasPrice": web3.to_wei("5", "gwei"),
        "nonce": web3.eth.get_transaction_count(account.address),
    }
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"Compounding TX Sent: {web3.to_hex(tx_hash)}")

if __name__ == "__main__":
    auto_compound()
