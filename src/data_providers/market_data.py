from .aave_provider import AaveDataProvider
from .sonic_provider import SonicDataProvider
import pandas as pd

class MarketDataAggregator:
    def __init__(self, arb_web3, sonic_web3):
        self.aave = AaveDataProvider(arb_web3)
        self.sonic = SonicDataProvider(sonic_web3)
        
    def get_market_data(self):
        """Aggregate all market data into a DataFrame"""
        return pd.DataFrame({
            'aave_apy': [self.aave.get_apy()],
            'sonic_apy': [self.sonic.get_apy()],
            'aave_tvl': [self.aave.get_tvl()],
            'sonic_tvl': [self.sonic.get_tvl()],
            'aave_rewards': [self.aave.get_rewards()],
            'sonic_rewards': [self.sonic.get_rewards()],
            'timestamp': [pd.Timestamp.now()]
        }) 