# from scripts.monitor_rewards import SmartRewardsMonitor
# from scripts.arbitrage_manager import ArbitrageManager
from web3 import Web3
import yaml
import asyncio
import logging
from dotenv import load_dotenv
import os
from src.agent.smart_agent import SmartAgent
from src.vault.super_vault_manager import SuperVaultManager, StrategyType
from src.data_providers.market_data import MarketDataAggregator
from src.data_providers.aave_provider import AaveDataProvider

class StrategyOrchestrator:
    def __init__(self):
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('StrategyOrchestrator')
        
        # Load configuration
        load_dotenv()
        with open("configs/config.yaml", "r") as f:
            self.config = yaml.safe_load(f)
            
        # Setup Sonic connection
        sonic_rpc_url = self.config["networks"]["sonic"]["rpc_url"]
        self.logger.info(f"Connecting to Sonic network at {sonic_rpc_url[:30]}...")
        self.sonic_web3 = Web3(Web3.HTTPProvider(sonic_rpc_url))
        
        # Setup Arbitrum connection
        arb_rpc_key = os.getenv("ARB_RPC_KEY", "6e80267c45670aebab0033a4eb5f354f96475310")
        arb_rpc_url = self.config["networks"]["arbitrum"]["rpc_url"].replace("${ARB_RPC_KEY}", arb_rpc_key)
        self.logger.info(f"Connecting to Arbitrum network at {arb_rpc_url[:30]}...")
        self.arb_web3 = Web3(Web3.HTTPProvider(arb_rpc_url))
        
        # Initialize managers with appropriate Web3 instances
        self.vault_manager = SuperVaultManager(
            self.sonic_web3,  # SuperVault is on Sonic
            self.config["contracts"]["supervault"]
        )
        
        self.agent = SmartAgent(
            self.sonic_web3,  # Primary Web3 for vault
            self.arb_web3,    # Secondary Web3 for Aave
            self.vault_manager
        )
        
        self.last_strategy_check = 0

    async def check_strategy_execution(self):
        """Check and execute strategy if needed"""
        try:
            current_time = asyncio.get_event_loop().time()
            
            # Check if it's time for strategy evaluation
            if current_time - self.last_strategy_check > self.config['strategy']['rebalance_interval']:
                self.logger.info("Analyzing market conditions...")
                
                # First check for emergency conditions
                emergency_actions = await self.agent.check_emergency_conditions()
                if emergency_actions:
                    self.logger.warning("Emergency conditions detected! Executing emergency actions...")
                    for action in emergency_actions:
                        await self.agent.execute_strategy(action)
                    return
                
                # Regular strategy analysis
                analysis = await self.agent.analyze_strategies()
                if analysis:
                    self.logger.info(f"Strategy recommendations: {analysis}")
                    for strategy in analysis:
                        self.logger.info(f"Executing strategy: {strategy}")
                        success = await self.agent.execute_strategy(strategy)
                        if success:
                            self.logger.info("Strategy executed successfully")
                        else:
                            self.logger.error("Strategy execution failed")
                
                self.last_strategy_check = current_time
            
        except Exception as e:
            self.logger.error(f"Error in strategy execution: {e}")

    async def monitor_balances(self):
        """Monitor balances and execute strategies"""
        try:
            total_assets = self.vault_manager.get_total_assets()
            self.logger.info(f"Total assets: {total_assets}")
            
            # Get strategy balances
            strategy1_balance = self.vault_manager.get_pool_balance(
                StrategyType.STRATEGY_1.value,
                self.config['contracts']['aave']['lending_token']
            )
            
            strategy2_balance = self.vault_manager.get_pool_balance(
                StrategyType.STRATEGY_2.value,
                self.config['contracts']['sonic']['wrapped_sonic']
            )
            
            self.logger.info(f"Strategy 1 balance: {strategy1_balance}")
            self.logger.info(f"Strategy 2 balance: {strategy2_balance}")
            
            # Properly await the async call
            await self.agent.rebalance_if_needed()
            
        except Exception as e:
            self.logger.error(f"Error monitoring balances: {e}")

    async def run(self):
        """Main loop"""
        try:
            check_interval = self.config.get('check_interval', 60)  # Default 60 seconds
            while True:
                await self.monitor_balances()
                await asyncio.sleep(check_interval)
                
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")

def main():
    try:
        orchestrator = StrategyOrchestrator()
        logging.getLogger('StrategyOrchestrator').info("""
            Strategy Orchestrator initialized:
            - SuperVault: 0x4BdE0740740b8dBb5f6Eb8c9ccB4Fc01171e953C
            - Strategy 1: 0xa1057829b37d1b510785881B2E87cC87fb4cccD3
            - Strategy 2: 0xC4012a3D99BC96637A03BF91A2e7361B1412FD17
        """)
        
        # Run the async event loop
        asyncio.run(orchestrator.run())
        
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main() 