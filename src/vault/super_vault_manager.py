from web3 import Web3
from enum import Enum
from typing import List, Tuple
import yaml
import json
import logging
import os
from eth_account import Account
import eth_account

class StrategyType(Enum):
    AAVE = 0
    BALANCER = 1
    STRATEGY_2 = 2

class SuperVaultManager:
    def __init__(self, web3: Web3, vault_address: str):
        self.web3 = web3
        self.vault_address = vault_address
        self.logger = logging.getLogger('SuperVaultManager')
        
        try:
            # Check if contract exists at address
            checksum_address = Web3.to_checksum_address(vault_address)
            code = self.web3.eth.get_code(checksum_address)
            if code == b'':
                raise Exception(f"No contract found at address {vault_address}")
            
            # Load SuperVault ABI
            with open("src/abis/SuperVault.json", "r") as f:
                self.vault_abi = json.load(f)
            
            # Store private key properly
            self.private_key = ''
            
            # Set up account
            account = Account.from_key(self.private_key)
            self.address = account.address
            
            # Initialize contract
            self.vault_contract = self.web3.eth.contract(
                address=checksum_address,
                abi=self.vault_abi
            )
            
            self.logger.info(f"Using account address: {self.address}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize vault: {e}")
            raise

    def _get_address_from_private_key(self, private_key: str) -> str:
        """Helper function to get the address from a private key"""
        try:
            # Clean up private key format
            private_key = private_key.strip()
            if private_key.startswith('0x'):
                private_key = private_key[2:]
            
            # Log the private key length for debugging
            self.logger.info(f"Private key length: {len(private_key)}")
            
            try:
                # Convert private key to bytes and create account
                account = self.web3.eth.account.from_key('')
                self.logger.info(f"Successfully derived address: {account.address}")
                return account.address
            
            except Exception as e:
                self.logger.error(f"Failed to convert private key to address: {e}")
                self.logger.error(f"Private key format incorrect. Should be 64 hex characters.")
                raise
            
        except Exception as e:
            self.logger.error(f"Error deriving address from private key: {e}")
            raise

    def get_vault_abi(self):
        """Get the vault ABI"""
        return self.vault_contract.functions.abi

    def get_total_assets(self):
        """Get total assets in the vault"""
        try:
            return self.vault_contract.functions.totalAssets().call()
        except Exception as e:
            self.logger.error(f"Error getting total assets: {e}")
            return 0

    def get_pool_balance(self, strategy_type: int, token_address: str):
        """Get balance of a specific pool"""
        try:
            # Convert strategy type to string name
            strategy_name = f"STRATEGY_{strategy_type}" if strategy_type > 0 else "AAVE"
            
            return self.vault_contract.functions.getPoolBalance(
                strategy_name,  # Pass string name instead of int
                Web3.to_checksum_address(token_address)
            ).call()
        except Exception as e:
            self.logger.error(f"Error getting pool balance: {e}")
            return 0

    def _check_agent_role(self):
        """Check if current account has AGENT_ROLE"""
        try:
            # Get the AGENT_ROLE bytes32 value
            AGENT_ROLE = self.vault_contract.functions.AGENT_ROLE().call()
            self.logger.info(f"AGENT_ROLE identifier: {AGENT_ROLE.hex()}")
            
            try:
                # Try to get the current agent using isAgent
                is_agent = self.vault_contract.functions.isAgent(self.address).call()
                
                if not is_agent:
                    self.logger.error(f"Account {self.address} is not the agent")
                    self.logger.info("Please ensure you're using the correct private key for address: 0x1655D65B58aB4a2646AA61693663B1685A20b319")
                    return False
                    
                self.logger.info(f"Account {self.address} is the agent")
                return True
                
            except Exception as e:
                self.logger.error(f"Could not verify agent status: {e}")
                # Log the derived address for debugging
                try:
                    private_key = ''
                    derived_address = self._get_address_from_private_key(private_key)
                    self.logger.info(f"Current private key corresponds to address: {private_key}")
                    self.logger.info(f"Current private key corresponds to address: {derived_address}")
                    self.logger.info(f"Expected agent address: 0x1655D65B58aB4a2646AA61693663B1685A20b319")
                except Exception as e2:
                    self.logger.error(f"Could not derive address from private key: {e2}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error checking agent role: {e}")
            return False

    def allocate_to_strategy(self, strategy_type, amount):
        """Allocate funds to a strategy"""
        try:
            self.logger.info(f"Current address: {self.address}")
            
            # Always use AAVE strategy (type 0)
            strategy_value = 0  # AAVE strategy
            self.logger.info(f"Using AAVE strategy (type {strategy_value})")
            
            # Check total assets first
            total_assets = self.vault_contract.functions.totalAssets().call()
            self.logger.info(f"Total assets in vault: {total_assets}")
            
            if amount > total_assets:
                raise Exception(f"Insufficient assets in vault. Have {total_assets}, need {amount}")
            
            # Get strategy address
            strategy_address = self.vault_contract.functions.getStrategyAddress(strategy_value).call()
            if strategy_address == '0x0000000000000000000000000000000000000000':
                raise Exception(f"Strategy {strategy_value} not found")
            
            self.logger.info(f"Strategy address: {strategy_address}")
            self.logger.info(f"Attempting to allocate: {amount}")
            
            # Build transaction
            function_call = self.vault_contract.functions.allocateToStrategy(
                strategy_value,  # Using AAVE strategy
                int(amount)
            )
            
            # Send transaction
            receipt = self._build_and_send_transaction(function_call)
            
            if receipt['status'] == 0:
                raise Exception("Transaction reverted")
            
            return receipt
            
        except Exception as e:
            self.logger.error(f"Failed to allocate to strategy: {str(e)}")
            raise
    
    def withdraw_from_strategy(self, strategy_type: StrategyType, amount: int):
        """Withdraw funds from a strategy"""
        return self.vault_contract.functions.withdrawFromStrategy(
            strategy_type.value,
            amount
        ).transact()
    
    def deposit_to_pool(self, pool_name: str, amount: int):
        """Deposit funds to a specific lending pool"""
        return self.vault_contract.functions.depositToPool(
            pool_name,
            amount
        ).transact()
    
    def withdraw_from_pool(self, pool_name: str, amount: int):
        """Withdraw funds from a specific lending pool"""
        return self.vault_contract.functions.withdrawFromPool(
            pool_name,
            amount
        ).transact()
    
    def get_pool_address(self, pool_name: str) -> str:
        """Get address of a specific pool"""
        return self.vault_contract.functions.getPoolAddress(pool_name).call()
    
    def get_pool_list(self) -> List[str]:
        """Get list of all pools"""
        return self.vault_contract.functions.getPoolList().call()
    
    def get_strategy_address(self, strategy_type: StrategyType) -> str:
        """Get address of a specific strategy"""
        return self.vault_contract.functions.getStrategyAddress(
            strategy_type.value
        ).call()
    
    def deposit(self, amount: int):
        """Deposit assets into the vault"""
        return self.vault_contract.functions.deposit(amount).transact()
    
    def withdraw(self, shares: int):
        """Withdraw assets from the vault"""
        return self.vault_contract.functions.withdraw(shares).transact()
    
    def set_agent(self, new_agent: str):
        """Set new agent address"""
        return self.vault_contract.functions.setAgent(new_agent).transact()
    
    def set_admin(self, new_admin: str):
        """Set new admin address"""
        return self.vault_contract.functions.setAdmin(new_admin).transact()

    def execute_function(self, target: str, data: bytes) -> Tuple[bool, bytes]:
        """Execute arbitrary function through vault (requires AGENT_ROLE)"""
        return self.vault_contract.functions.executeFunction(target, data).call()
    
    def _compare_yields(self):
        """Compare yields across different protocols"""
        current = self.historical_data.iloc[-1]
        
        # Calculate real yields (APY + rewards)
        aave_real_yield = current['aave_apy'] + current['aave_rewards']
        sonic_real_yield = current['sonic_apy'] + current['sonic_rewards']
        
        return {
            'highest_yield': max(aave_real_yield, sonic_real_yield),
            'yield_diff': aave_real_yield - sonic_real_yield,
            'recommended_protocol': 'Aave' if aave_real_yield > sonic_real_yield else 'Sonic'
        }
    
    def _assess_risk(self, aave_position):
        """Assess current risk levels"""
        return {
            'health_factor': aave_position['health_factor'],
            'risk_level': self._calculate_risk_level(aave_position),
            'suggested_adjustments': self._get_risk_adjustments(aave_position)
        }
    
    def _calculate_risk_level(self, position):
        if position['health_factor'] > 2.0:
            return 'low'
        elif position['health_factor'] > 1.5:
            return 'medium'
        else:
            return 'high'
    
    def _get_risk_adjustments(self, position):
        adjustments = []
        
        if position['health_factor'] < 1.5:
            adjustments.append("Reduce borrowed amount")
        if position['estimated_net_apy'] < 0:
            adjustments.append("Consider closing positions")
        
        return adjustments

    def _build_and_send_transaction(self, function_call):
        """Helper method to build and send transactions"""
        try:
            # Get current gas price and add 20% buffer
            gas_price = int(self.web3.eth.gas_price * 1.2)
            
            # Build transaction with higher gas limit
            tx = function_call.build_transaction({
                'from': self.address,
                'nonce': self.web3.eth.get_transaction_count(self.address),
                'gas': 1000000,  # Increased gas limit
                'gasPrice': gas_price,
                'chainId': self.web3.eth.chain_id
            })
            
            self.logger.info(f"Transaction params: gas={tx['gas']}, gasPrice={tx['gasPrice']}")
            
            # Sign and send
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            self.logger.info(f"Transaction sent with hash: {tx_hash.hex()}")
            
            # Wait for receipt with longer timeout
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
            
            if receipt['status'] == 0:
                # Get revert reason if possible
                try:
                    tx_details = self.web3.eth.call(tx)
                    self.logger.error(f"Transaction reverted with: {tx_details}")
                except Exception as e:
                    self.logger.error(f"Could not get revert reason: {str(e)}")
            
            return receipt
            
        except Exception as e:
            self.logger.error(f"Transaction failed: {str(e)}")
            raise