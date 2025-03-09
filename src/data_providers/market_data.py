from src.data_providers.aave_provider import AaveDataProvider
import pandas as pd
import logging

class MarketDataAggregator:
    def __init__(self, web3):
        self.logger = logging.getLogger('MarketDataAggregator')
        self.web3 = web3
        self.aave = AaveDataProvider(web3)
        
    def get_market_data(self):
        """Aggregate all market data into a DataFrame"""
        try:
            aave_data = self.aave.get_optimal_position()
            return {
                'aave': {
                    'supply_apy': aave_data['supply_apy'],
                    'borrow_apy': aave_data['borrow_apy'],
                    'net_apy': aave_data['estimated_net_apy'],
                    'utilization': aave_data['utilization_rate'],
                    'health_factor': aave_data['health_factor'],
                    'tvl': self.aave.get_total_tvl()
                },
                'sonic': {
                    'wrapped_price': self._get_sonic_price(),
                    'tvl': self._get_sonic_tvl(),
                    'volume_24h': self._get_sonic_volume()
                },
                'timestamp': pd.Timestamp.now()
            }
        except Exception as e:
            self.logger.error(f"Error getting market data: {e}")
            return {}
            
    def _get_sonic_price(self):
        """Get Sonic token price"""
        try:
            # TODO: Implement real price fetch
            return 1.0
        except Exception as e:
            self.logger.error(f"Error getting Sonic price: {e}")
            return 0
            
    def _get_sonic_tvl(self):
        """Get Sonic TVL"""
        try:
            # TODO: Implement real TVL fetch
            return 1000000
        except Exception as e:
            self.logger.error(f"Error getting Sonic TVL: {e}")
            return 0
            
    def _get_sonic_volume(self):
        """Get Sonic 24h volume"""
        try:
            # TODO: Implement real volume fetch
            return 500000
        except Exception as e:
            self.logger.error(f"Error getting Sonic volume: {e}")
            return 0
            
    def get_aave_data(self):
        """Get Aave specific data"""
        try:
            return {
                'lending_rate': self.aave.get_lending_apy(),
                'pool_address': self.aave.get_aave_pool_address(),
                'lending_token': self.aave.get_lending_token_address()
            }
        except Exception as e:
            self.logger.error(f"Error getting Aave data: {e}")
            return {} 