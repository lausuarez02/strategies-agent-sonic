from scripts.monitor_rewards import SmartRewardsMonitor
from scripts.arbitrage_manager import ArbitrageManager
from web3 import Web3
import yaml
import asyncio
import logging
from dotenv import load_dotenv
import os
from agent.smart_agent import SmartAgent

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
            
        # Initialize Web3 connections
        self.setup_web3_connections()
        
        # Initialize components
        self.agent = SmartAgent(self.arb_web3, self.sonic_web3)
        self.arbitrage_manager = ArbitrageManager(
            self.arb_web3,
            self.sonic_web3,
            vault_percentage=self.config['strategy']['arbitrage']['vault_percentage']
        )

    def setup_web3_connections(self):
        """Initialize Web3 connections to both chains"""
        # Setup Sonic connection
        self.sonic_web3 = Web3(Web3.HTTPProvider(
            self.config["networks"]["sonic"]["rpc_url"]
        ))
        
        # Setup Arbitrum connection
        arb_rpc = self.config["networks"]["arbitrum"]["rpc_url"].replace(
            "${ARB_RPC_KEY}", 
            os.getenv("ARB_RPC_KEY")
        )
        self.arb_web3 = Web3(Web3.HTTPProvider(arb_rpc))

    async def run_arbitrage_monitoring(self):
        """Continuous arbitrage monitoring loop"""
        while True:
            try:
                self.logger.info("Checking arbitrage opportunities...")
                arb_opportunity = self.arbitrage_manager.find_arbitrage_opportunities()
                
                if arb_opportunity['is_profitable']:
                    self.logger.info(f"Found profitable arbitrage! Difference: {arb_opportunity['price_difference']:.2%}")
                    await self.arbitrage_manager.execute_arbitrage(
                        arb_opportunity['min_profitable_amount']
                    )
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in arbitrage monitoring: {e}")
                await asyncio.sleep(60)

    async def run_agent_monitoring(self):
        """Continuous agent monitoring loop"""
        while True:
            try:
                self.logger.info("Agent analyzing market conditions...")
                recommendation = self.agent.get_recommendation()
                
                self.logger.info(f"Agent recommendations: {recommendation['recommendations']}")
                
                # Execute recommendations if needed
                # This would need implementation based on your specific needs
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"Error in agent monitoring: {e}")
                await asyncio.sleep(300)

    async def run(self):
        """Main execution loop"""
        self.logger.info("Starting Strategy Orchestrator...")
        
        # Create tasks for different monitoring loops
        tasks = [
            self.run_arbitrage_monitoring(),
            self.run_agent_monitoring()  # Replace rewards monitoring with agent monitoring
        ]
        
        # Run all tasks concurrently
        await asyncio.gather(*tasks)

def main():
    orchestrator = StrategyOrchestrator()
    
    # Run the async event loop
    try:
        asyncio.run(orchestrator.run())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main() 