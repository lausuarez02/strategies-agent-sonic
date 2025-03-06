from web3 import Web3
import yaml
from data_providers.market_data import MarketDataAggregator
from web3.sonic import estimate_gas_cost

class ArbitrageManager:
    def __init__(self, arb_web3, sonic_web3, vault_percentage=0.05):
        self.arb_web3 = arb_web3
        self.sonic_web3 = sonic_web3
        self.vault_percentage = vault_percentage  # Percentage of vault to use for arbitrage
        self.market_data = MarketDataAggregator(arb_web3, sonic_web3)
        
        # Load config
        with open("configs/config.yaml", "r") as f:
            self.config = yaml.safe_load(f)
            
    def find_arbitrage_opportunities(self):
        """Find price differences between Sonic and Arbitrum"""
        market_data = self.market_data.get_market_data()
        
        # Get prices from both chains
        sonic_price = market_data['sonic_price']
        arb_price = market_data['arbitrum_price']
        
        # Calculate price difference percentage
        price_diff = abs(sonic_price - arb_price) / min(sonic_price, arb_price)
        
        # Estimate transaction costs
        sonic_tx_cost = estimate_gas_cost(self.sonic_web3, self._build_sample_tx())
        arb_tx_cost = estimate_gas_cost(self.arb_web3, self._build_sample_tx())
        total_tx_cost = sonic_tx_cost['cost_usd'] + arb_tx_cost['cost_usd']
        
        # Calculate minimum profitable amount
        min_profitable_amount = total_tx_cost / price_diff
        
        return {
            'price_difference': price_diff,
            'transaction_costs': total_tx_cost,
            'min_profitable_amount': min_profitable_amount,
            'is_profitable': price_diff > (total_tx_cost * 1.05)  # 5% minimum profit margin
        }
    
    def execute_arbitrage(self, amount):
        """Execute arbitrage if profitable"""
        opportunity = self.find_arbitrage_opportunities()
        
        if opportunity['is_profitable'] and amount >= opportunity['min_profitable_amount']:
            # Execute trades on both chains
            try:
                # Execute first leg of arbitrage
                if self.sonic_price > self.arb_price:
                    self._sell_on_sonic(amount)
                    self._buy_on_arbitrum(amount)
                else:
                    self._sell_on_arbitrum(amount)
                    self._buy_on_sonic(amount)
                    
                return True
            except Exception as e:
                print(f"Arbitrage execution failed: {e}")
                return False
                
        return False 