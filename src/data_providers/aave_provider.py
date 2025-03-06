from web3 import Web3
import yaml
import os

class AaveDataProvider:
    def __init__(self, web3_instance):
        self.web3 = web3_instance
        with open("configs/config.yaml", "r") as f:
            self.config = yaml.safe_load(f)
        
        # Get Aave addresses from config
        aave_config = self.config["contracts"]["arbitrum"]["aave"]
        self.AAVE_POOL = aave_config["pool"]
        self.AAVE_POOL_DATA_PROVIDER = aave_config["pool_data_provider"]
        self.ETH = aave_config["tokens"]["eth"]
        self.USDC = aave_config["tokens"]["usdc"]
        
        # Initialize Aave contracts
        self.pool = self.web3.eth.contract(
            address=self.AAVE_POOL,
            abi=self.get_aave_pool_abi()
        )
        
        self.data_provider = self.web3.eth.contract(
            address=self.AAVE_POOL_DATA_PROVIDER,
            abi=self.get_data_provider_abi()
        )

    def get_eth_usdc_strategy_data(self):
        """Get data for ETH collateral -> USDC borrow strategy"""
        # Get ETH supply data
        eth_data = self.data_provider.functions.getReserveData(self.ETH).call()
        eth_supply_apy = eth_data[3] / 1e27  # Convert RAY to percentage
        
        # Get USDC borrow data
        usdc_data = self.data_provider.functions.getReserveData(self.USDC).call()
        usdc_borrow_apy = usdc_data[4] / 1e27  # Variable borrow rate
        
        # Get user configuration
        user_data = self.pool.functions.getUserAccountData(self.config["wallet_address"]).call()
        
        return {
            'eth_supply_apy': eth_supply_apy,
            'usdc_borrow_apy': usdc_borrow_apy,
            'total_collateral_eth': user_data[0] / 1e18,
            'total_debt_eth': user_data[1] / 1e18,
            'available_borrow_eth': user_data[2] / 1e18,
            'current_ltv': user_data[3] / 1e4,  # Current Loan to Value
            'health_factor': user_data[5] / 1e18
        }

    def get_optimal_position(self):
        """Calculate optimal ETH collateral and USDC borrow amounts"""
        data = self.get_eth_usdc_strategy_data()
        
        # Conservative LTV of 65% (max is usually 82.5% for ETH)
        target_ltv = 0.65
        
        # Get ETH price in USD
        eth_price = self.get_eth_price()
        
        # Calculate optimal amounts
        eth_collateral = data['total_collateral_eth']
        max_usdc_borrow = (eth_collateral * eth_price * target_ltv)
        
        return {
            'suggested_eth_collateral': eth_collateral,
            'suggested_usdc_borrow': max_usdc_borrow,
            'estimated_net_apy': data['eth_supply_apy'] - data['usdc_borrow_apy'],
            'health_factor': data['health_factor']
        }

    def get_eth_price(self):
        """Get ETH price from Aave Oracle"""
        oracle = self.web3.eth.contract(
            address=self.config["contracts"]["arbitrum"]["aave"]["oracle"],
            abi=self.get_oracle_abi()
        )
        return oracle.functions.getAssetPrice(self.ETH).call() / 1e8

    def get_aave_pool_abi(self):
        """Minimal ABI for Aave Pool"""
        return [
            {
                "inputs": [{"type": "address"}],
                "name": "getUserAccountData",
                "outputs": [
                    {"type": "uint256"},  # totalCollateralETH
                    {"type": "uint256"},  # totalDebtETH
                    {"type": "uint256"},  # availableBorrowsETH
                    {"type": "uint256"},  # currentLiquidationThreshold
                    {"type": "uint256"},  # ltv
                    {"type": "uint256"}   # healthFactor
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]

    # ... other ABI getters ...

    def get_apy(self):
        """Get current Aave lending APY"""
        eth_data = self.data_provider.functions.getReserveData(self.ETH).call()
        return eth_data[3] / 1e27  # Convert RAY to percentage
        
    def get_rewards(self):
        """Get pending Aave rewards"""
        # Note: For Aave v3, rewards are handled by the RewardsController contract
        rewards_controller = self.config["contracts"]["arbitrum"]["aave"]["rewards_controller"]
        try:
            rewards_contract = self.web3.eth.contract(
                address=rewards_controller,
                abi=self.get_rewards_abi()
            )
            pending_rewards = rewards_contract.functions.getUserRewards(
                [self.ETH],  # List of assets to check
                self.config["wallet_address"],  # User address
                "0x0000000000000000000000000000000000000000"  # Reward token (0x0 for default)
            ).call()
            return pending_rewards / 1e18  # Convert to human readable
        except Exception as e:
            print(f"Error fetching rewards: {e}")
            return 0
        
    def get_tvl(self):
        """Get Total Value Locked in Aave"""
        eth_data = self.data_provider.functions.getReserveData(self.ETH).call()
        total_supply = eth_data[0]  # Total supply in the reserve
        eth_price = self.get_eth_price()
        return (total_supply * eth_price) / 1e18  # Convert to USD value

    def get_rewards_abi(self):
        """Minimal ABI for Aave Rewards Controller"""
        return [
            {
                "inputs": [
                    {"type": "address[]"},  # assets
                    {"type": "address"},    # user
                    {"type": "address"}     # reward token
                ],
                "name": "getUserRewards",
                "outputs": [{"type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]

    def get_data_provider_abi(self):
        """Minimal ABI for Aave Pool Data Provider"""
        return [
            {
                "inputs": [{"type": "address"}],
                "name": "getReserveData",
                "outputs": [
                    {"type": "uint256"},  # totalLiquidity
                    {"type": "uint256"},  # availableLiquidity
                    {"type": "uint256"},  # totalBorrows
                    {"type": "uint256"},  # availableBorrows
                    {"type": "uint256"},  # reserveFactor
                    {"type": "uint256"},  # variableBorrowRate
                    {"type": "uint256"},  # stableBorrowRate
                    {"type": "uint256"},  # liquidityRate
                    {"type": "uint256"},  # variableBorrowIndex
                    {"type": "uint256"},  # stableBorrowIndex
                    {"type": "uint256"},  # lastUpdateTimestamp
                    {"type": "uint256"}   # aTokenAddress
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]

    def get_oracle_abi(self):
        """Minimal ABI for Aave Oracle"""
        return [
            {
                "inputs": [{"type": "address"}],
                "name": "getAssetPrice",
                "outputs": [{"type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]

    def get_data_provider_abi(self):
        """Minimal ABI for Aave Pool Data Provider"""
        return [
            {
                "inputs": [{"type": "address"}],
                "name": "getReserveData",
                "outputs": [
                    {"type": "uint256"},  # totalLiquidity
                    {"type": "uint256"},  # availableLiquidity
                    {"type": "uint256"},  # totalBorrows
                    {"type": "uint256"},  # availableBorrows
                    {"type": "uint256"},  # reserveFactor
                    {"type": "uint256"},  # variableBorrowRate
                    {"type": "uint256"},  # stableBorrowRate
                    {"type": "uint256"},  # liquidityRate
                    {"type": "uint256"},  # variableBorrowIndex
                    {"type": "uint256"},  # stableBorrowIndex
                    {"type": "uint256"},  # lastUpdateTimestamp
                    {"type": "uint256"}   # aTokenAddress
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]

    def get_oracle_abi(self):
        """Minimal ABI for Aave Oracle"""
        return [
            {
                "inputs": [{"type": "address"}],
                "name": "getAssetPrice",
                "outputs": [{"type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            }
        ] 