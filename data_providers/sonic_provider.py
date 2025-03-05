from web3 import Web3
import yaml
import os

class SonicDataProvider:
    def __init__(self, web3_instance):
        self.web3 = web3_instance
        with open("configs/config.yaml", "r") as f:
            self.config = yaml.safe_load(f)
            
        # Initialize Sonic contracts here
        
    def get_apy(self):
        """Get current Sonic farming APY"""
        pass
        
    def get_rewards(self):
        """Get pending Sonic rewards"""
        pass
        
    def get_tvl(self):
        """Get Total Value Locked in Sonic"""
        pass 