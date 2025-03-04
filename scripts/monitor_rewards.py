from web3.sonic import get_rewards
import time

THRESHOLD = 0.05  # Auto-compound if rewards exceed 5%

def monitor():
    while True:
        rewards = get_rewards()
        print(f"Current rewards: {rewards} ETH")

        if rewards > THRESHOLD:
            print("Triggering auto-compounding...")
            # Call auto_compound.py (or send a tx)
        
        time.sleep(3600)  # Check every hour

if __name__ == "__main__":
    monitor()
