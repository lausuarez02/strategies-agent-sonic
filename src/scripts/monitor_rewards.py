from web3 import Web3
from dotenv import load_dotenv
import yaml
import time
import os
from ai.agent import AIAgent
import pandas as pd
from data_providers.market_data import MarketDataAggregator
from scripts.arbitrage_manager import ArbitrageManager

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

        # Add arbitrage manager
        self.arbitrage_manager = ArbitrageManager(
            self.arb_web3,
            self.sonic_web3,
            vault_percentage=0.05  # Use 5% of vault for arbitrage
        )

        # Separate monitoring intervals
        self.ARBITRAGE_CHECK_INTERVAL = 30  # Check every 30 seconds
        self.last_rebalance_time = time.time()

    def monitor_and_execute(self):
        while True:
            try:
                current_time = time.time()
                
                # Always check arbitrage opportunities (high frequency)
                arb_opportunity = self.arbitrage_manager.find_arbitrage_opportunities()
                if arb_opportunity['is_profitable']:
                    vault_balance = self.vault_manager.get_total_balance()
                    arb_amount = vault_balance * self.arbitrage_manager.vault_percentage
                    
                    if arb_amount >= arb_opportunity['min_profitable_amount']:
                        print(f"Executing arbitrage with {arb_amount} tokens...")
                        self.arbitrage_manager.execute_arbitrage(arb_amount)
                
                # Check if it's time for regular rebalancing (low frequency)
                if current_time - self.last_rebalance_time >= self.config['strategy']['rebalance_interval']:
                    # Collect market data for rebalancing
                    market_data = self.collect_market_data()
                    should_execute = self.ai_agent.execute_strategy(market_data)
                    
                    if should_execute:
                        print("AI recommends strategy execution!")
                        aave_rewards = self.get_aave_rewards()
                        sonic_rewards = self.get_sonic_rewards()
                        
                        if self.should_compound(aave_rewards, sonic_rewards):
                            print("Executing rebalancing strategy...")
                            self.vault_manager.execute_cross_chain_strategy(
                                amount=self.calculate_optimal_amount()
                            )
                    
                    self.last_rebalance_time = current_time
                
                # Short sleep for arbitrage monitoring
                time.sleep(self.ARBITRAGE_CHECK_INTERVAL)
                
            except Exception as e:
                print(f"Error in monitoring: {e}")
                time.sleep(60)  # Longer sleep on error

    def collect_market_data(self):
        """Collect market data using the aggregator"""
        return self.market_data.get_market_data()

    # ... rest of monitoring functions ...

if __name__ == "__main__":
    monitor = SmartRewardsMonitor()
    monitor.monitor_and_execute()
