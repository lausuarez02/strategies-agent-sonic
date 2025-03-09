from web3 import Web3
from ..vault.super_vault_manager import SuperVaultManager, StrategyType
import yaml
import os
import logging
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoCompounder:
    def __init__(self):
        # Load Config
        with open("configs/config.yaml", "r") as f:
            self.config = yaml.safe_load(f)

        # Initialize Web3
        self.web3 = Web3(Web3.HTTPProvider(self.config["networks"]["arbitrum"]["rpc_url"]))
        
        # Setup account
        self.private_key = os.getenv("PRIVATE_KEY") or self.config["networks"]["arbitrum"]["private_key"]
        self.account = self.web3.eth.account.from_key(self.private_key)
        
        # Initialize vault manager
        self.vault_manager = SuperVaultManager(
            self.web3,
            self.config["contracts"]["arbitrum"]["super_vault"]
        )

    async def check_compound_opportunity(self) -> Optional[Dict]:
        """Check if compounding is profitable"""
        try:
            # Get current pool balances
            pool_list = self.vault_manager.get_pool_list()
            total_rewards = 0
            
            for pool_name in pool_list:
                pool_balance = self.vault_manager.get_pool_balance(
                    pool_name,
                    self.config["contracts"]["arbitrum"]["aave"]["tokens"]["eth"]
                )
                if pool_balance > 0:
                    # Calculate rewards for this pool
                    rewards = self._calculate_pool_rewards(pool_name, pool_balance)
                    total_rewards += rewards
            
            # Check if rewards meet minimum threshold
            min_reward = self.config["strategy"].get("min_compound_reward", 0.01)
            
            if total_rewards > min_reward:
                return {
                    "should_compound": True,
                    "total_rewards": total_rewards,
                    "estimated_gas": 200000  # Base estimate, could be dynamic
                }
            
            return None

        except Exception as e:
            logger.error(f"Error checking compound opportunity: {e}")
            return None

    async def auto_compound(self):
        """Execute auto-compounding if profitable"""
        try:
            opportunity = await self.check_compound_opportunity()
            
            if not opportunity:
                logger.info("No profitable compounding opportunity found")
                return
            
            logger.info(f"Found compounding opportunity. Rewards: {opportunity['total_rewards']} ETH")
            
            # Get current gas price
            gas_price = self.web3.eth.gas_price
            
            # Estimate total gas cost
            gas_cost = gas_price * opportunity['estimated_gas']
            gas_cost_eth = self.web3.from_wei(gas_cost, 'ether')
            
            # Check if compounding is profitable after gas
            if gas_cost_eth >= opportunity['total_rewards']:
                logger.info(f"Compounding not profitable after gas. Cost: {gas_cost_eth} ETH")
                return
            
            # Execute compounding through vault manager
            logger.info("Executing compound transaction...")
            
            # Compound rewards back into the strategy
            await self.vault_manager.allocate_to_strategy(
                StrategyType.AAVE,
                self.web3.to_wei(opportunity['total_rewards'], 'ether')
            )
            
            logger.info("Successfully compounded rewards")

        except Exception as e:
            logger.error(f"Error in auto_compound: {e}")

    def _calculate_pool_rewards(self, pool_name: str, balance: int) -> float:
        """Calculate unclaimed rewards for a specific pool"""
        # Implementation will depend on specific pool reward calculation
        # This is a placeholder that should be implemented based on the specific pool
        pass

if __name__ == "__main__":
    import asyncio
    
    async def main():
        compounder = AutoCompounder()
        while True:
            await compounder.auto_compound()
            # Wait for next check interval (e.g., every hour)
            await asyncio.sleep(3600)
    
    asyncio.run(main()) 