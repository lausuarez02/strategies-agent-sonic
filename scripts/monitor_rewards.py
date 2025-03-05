from web3 import Web3
from dotenv import load_dotenv
import yaml
import time
import os
from ai.agent import AIAgent
import pandas as pd
from data_providers.market_data import MarketDataAggregator

class SmartRewardsMonitor:
    def __init__(self):
        # Initialize Web3 and contracts
        load_dotenv()
        self.setup_web3()
        
        # Initialize AI Agent
        self.ai_agent = AIAgent(
            'models/yield_predictor.pkl',
            'models/risk_analyzer.pkl'
        )
        
        # Initialize strategy executor
        self.vault_manager = SuperVaultManager()
        
        # Initialize data provider
        self.market_data = MarketDataAggregator(
            self.arb_web3,
            self.sonic_web3
        )

    def monitor_and_execute(self):
        while True:
            try:
                # Collect market data
                market_data = self.collect_market_data()
                
                # Get AI decision
                should_execute = self.ai_agent.execute_strategy(market_data)
                
                if should_execute:
                    print("AI recommends strategy execution!")
                    
                    # Get current rewards/APY
                    aave_rewards = self.get_aave_rewards()
                    sonic_rewards = self.get_sonic_rewards()
                    
                    # If profitable, execute
                    if self.should_compound(aave_rewards, sonic_rewards):
                        print("Executing strategy...")
                        self.vault_manager.execute_cross_chain_strategy(
                            amount=self.calculate_optimal_amount()
                        )
                
                time.sleep(3600)  # Check every hour
                
            except Exception as e:
                print(f"Error in monitoring: {e}")
                time.sleep(60)

    def collect_market_data(self):
        """Collect market data using the aggregator"""
        return self.market_data.get_market_data()

    # ... rest of monitoring functions ...

if __name__ == "__main__":
    monitor = SmartRewardsMonitor()
    monitor.monitor_and_execute()
