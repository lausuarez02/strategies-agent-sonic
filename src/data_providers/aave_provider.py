from web3 import Web3
import json
import logging

class AaveDataProvider:
    def __init__(self, web3: Web3):
        self.web3 = web3
        self.logger = logging.getLogger('AaveDataProvider')
        
        # Load Aave Pool ABI
        with open("src/abis/AavePool.json", "r") as f:
            self.aave_pool_abi = json.load(f)
            
        # Initialize contract addresses
        self.AAVE_POOL = "0x794a61358D6845594F94dc1DB02A252b5b4814aD"
        self.LENDING_TOKEN = "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8"
        
        # Initialize contracts
        self.aave_pool = self.web3.eth.contract(
            address=self.AAVE_POOL,
            abi=self.aave_pool_abi
        )

    def get_lending_token_address(self):
        """Get the lending token address (USDC)"""
        return self.LENDING_TOKEN

    def get_aave_pool_address(self):
        """Get the Aave pool address"""
        return self.AAVE_POOL

    def get_user_data(self, user_address: str):
        """Get user account data from Aave"""
        try:
            user_data = self.aave_pool.functions.getUserAccountData(user_address).call()
            return {
                'total_collateral_eth': user_data[0],
                'total_debt_eth': user_data[1],
                'available_borrow_eth': user_data[2],
                'current_liquidation_threshold': user_data[3],
                'ltv': user_data[4],
                'health_factor': user_data[5]
            }
        except Exception as e:
            self.logger.error(f"Error getting user data: {e}")
            return None

    def get_reserve_data(self, asset_address: str):
        """Get reserve data for an asset"""
        try:
            reserve_data = self.aave_pool.functions.getReserveData(asset_address).call()
            return {
                'liquidity_rate': reserve_data[0],  # Supply APY
                'variable_borrow_rate': reserve_data[1],
                'stable_borrow_rate': reserve_data[2],
                'liquidity_index': reserve_data[3],
                'variable_borrow_index': reserve_data[4]
            }
        except Exception as e:
            self.logger.error(f"Error getting reserve data: {e}")
            return None

    def get_rewards(self):
        """Get current rewards APR for lending"""
        try:
            # This is a simplified version - you might need to implement
            # specific reward calculation logic based on your needs
            reserve_data = self.get_reserve_data(self.LENDING_TOKEN)
            if reserve_data:
                # Convert to percentage (APR)
                return Web3.from_wei(reserve_data['liquidity_rate'], 'ether') * 100
            return 0
        except Exception as e:
            self.logger.error(f"Error getting rewards: {e}")
            return 0

    def get_lending_apy(self):
        """Get current lending APY"""
        try:
            reserve_data = self.get_reserve_data(self.LENDING_TOKEN)
            if reserve_data:
                # Convert to percentage (APY)
                return Web3.from_wei(reserve_data['liquidity_rate'], 'ether') * 100
            return 0
        except Exception as e:
            self.logger.error(f"Error getting lending APY: {e}")
            return 0

    def get_total_tvl(self):
        """Get total TVL in Aave"""
        try:
            reserve_data = self.get_reserve_data(self.LENDING_TOKEN)
            if reserve_data:
                return reserve_data['liquidity_index'] / 1e6  # Convert from USDC decimals
            return 0
        except Exception as e:
            self.logger.error(f"Error getting TVL: {e}")
            return 0

    def get_optimal_position(self):
        """Get optimal position data from Aave"""
        try:
            reserve_data = self.get_reserve_data(self.LENDING_TOKEN)
            if not reserve_data:
                raise Exception("Failed to get reserve data")
                
            return {
                'supply_apy': reserve_data['liquidity_rate'] / 1e27,
                'borrow_apy': reserve_data['variable_borrow_rate'] / 1e27,
                'estimated_net_apy': (reserve_data['liquidity_rate'] - reserve_data['variable_borrow_rate']) / 1e27,
                'utilization_rate': reserve_data['liquidity_index'] / (reserve_data['liquidity_index'] + reserve_data['variable_borrow_index']),
                'health_factor': 1.5,  # Default safe value
                'borrow_ratio': 0.0  # Placeholder
            }
        except Exception as e:
            self.logger.error(f"Error getting optimal position: {e}")
            return {
                'supply_apy': 0,
                'borrow_apy': 0,
                'estimated_net_apy': 0,
                'utilization_rate': 0,
                'health_factor': 0,
                'borrow_ratio': 0
            } 