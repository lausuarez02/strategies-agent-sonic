from src.data_providers.market_data import MarketDataAggregator
from src.data_providers.aave_provider import AaveDataProvider
from src.data_providers.protocol_data.aggregator import ProtocolDataAggregator
from src.vault.super_vault_manager import SuperVaultManager, StrategyType
import pandas as pd
import logging
from src.agent.knowledge_box import KnowledgeBox  # Add this import
import yaml
from enum import Enum
from web3 import Web3
from eth_abi.abi import encode
import json
from openai import OpenAI  # Add this import at the top
import os

class StrategyType(Enum):
    AAVE = 0
    STRATEGY_1 = 1
    STRATEGY_2 = 2

class SmartAgent:
    def __init__(self, sonic_web3, arb_web3, vault_manager: SuperVaultManager):
        self.logger = logging.getLogger('SmartAgent')
        self.sonic_web3 = sonic_web3
        self.arb_web3 = arb_web3
        
        # Load configuration
        with open("configs/config.yaml", "r") as f:
            self.config = yaml.safe_load(f)
            
        self.vault_manager = vault_manager
        self.market_data = MarketDataAggregator(self.arb_web3)  # Aave data from Arbitrum
        self.aave = AaveDataProvider(self.arb_web3)  # Aave interactions on Arbitrum
        self.protocol_data = ProtocolDataAggregator(self.arb_web3)
        
        # Initialize historical data storage
        self.historical_data = pd.DataFrame()
        
        # Initialize knowledge box
        self.knowledge = KnowledgeBox()
        
        # Initialize contract addresses
        self.SUPER_VAULT = "0x4BdE0740740b8dBb5f6Eb8c9ccB4Fc01171e953C"
        self.STRATEGY_1 = "0xa1057829b37d1b510785881B2E87cC87fb4cccD3"
        self.STRATEGY_2 = "0xC4012a3D99BC96637A03BF91A2e7361B1412FD17"
        
        # Initialize SuperVault contract with Sonic web3 instead of Arbitrum
        with open("src/abis/SuperVault.json", "r") as f:
            abi_data = json.load(f)
            self.vault_abi = abi_data if isinstance(abi_data, list) else abi_data.get('abi', [])
        self.vault_contract = self.sonic_web3.eth.contract(
            address=Web3.to_checksum_address(self.SUPER_VAULT),
            abi=self.vault_abi
        )

        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        if not os.getenv('OPENAI_API_KEY'):
            self.logger.warning("OpenAI API key not found. AI features will be disabled.")

        # Validate strategy parameters
        if not self._validate_strategy_params():
            self.logger.warning("Invalid strategy parameters")

        agent_balance = self.arb_web3.eth.get_balance("0x1655D65B58aB4a2646AA61693663B1685A20b319")
        print(f"Agent ETH Balance: {self.arb_web3.from_wei(agent_balance, 'ether')} ETH")

    def _validate_strategy_params(self):
        """Validate strategy configuration parameters"""
        try:
            required_params = {
                'min_apy': 0.05,
                'max_allocation_percentage': 0.8,
                'rebalance_threshold': 0.05
            }
            
            strategy_config = self.config.get('strategy', {})
            for param, default in required_params.items():
                if param not in strategy_config:
                    strategy_config[param] = default
                    self.logger.info(f"Using default value for {param}: {default}")
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating strategy parameters: {e}")
            return False

    async def analyze_market_conditions(self):
        """Analyze current market conditions"""
        try:
            aave_data = self.aave.get_optimal_position()
            market_data = self.market_data.get_market_data()
            
            # Ensure we have valid data
            if not aave_data or not market_data:
                self.logger.error("Failed to get market data")
                return {
                    'metrics': {
                        'aave_apy': 0,
                        'health_factor': 0,
                        'utilization': 0
                    },
                    'optimal_allocation': 0
                }
            
            # Log the data we're working with
            self.logger.info(f"AAVE data: {aave_data}")
            self.logger.info(f"Market data: {market_data}")
            
            return {
                'metrics': {
                    'aave_apy': aave_data['estimated_net_apy'],
                    'health_factor': aave_data['health_factor'],
                    'utilization': aave_data['utilization_rate'],
                    'sonic_apy': market_data.get('sonic', {}).get('apy', 0)
                },
                'optimal_allocation': self._calculate_optimal_allocation({
                    'aave_apy': aave_data['estimated_net_apy'],
                    'sonic_apy': market_data.get('sonic', {}).get('apy', 0)
                })
            }
        except Exception as e:
            self.logger.error(f"Error analyzing market conditions: {e}")
            return {
                'metrics': {
                    'aave_apy': 0,
                    'health_factor': 0,
                    'utilization': 0,
                    'sonic_apy': 0
                },
                'optimal_allocation': 0
            }
    
    def execute_strategy(self, strategy):
        """Execute a given strategy"""
        try:
            self.logger.info(f"Executing strategy: {strategy}")
            
            # Validate strategy parameters
            if not strategy.get('type') or not strategy.get('allocate_amount'):
                raise ValueError("Invalid strategy parameters")
                
            # Get current balances
            total_assets = self.vault_manager.get_total_assets()
            self.logger.info(f"Current total assets: {total_assets}")
            
            # Check if amount is reasonable
            if strategy['allocate_amount'] > total_assets:
                self.logger.warning("Strategy amount exceeds total assets")
                return False
                
            # Convert strategy type to int value if it's an enum
            strategy_type = strategy['type'].value if hasattr(strategy['type'], 'value') else strategy['type']
                
            # Execute based on strategy type
            if strategy_type in [StrategyType.AAVE.value, StrategyType.STRATEGY_1.value]:
                success = self._execute_aave_strategy(strategy)
            elif strategy_type == StrategyType.STRATEGY_2.value:
                success = self._execute_sonic_strategy(strategy)
            else:
                self.logger.error(f"Unknown strategy type: {strategy['type']}")
                return False
                
            return success
            
        except Exception as e:
            self.logger.error(f"Error executing strategy: {e}")
            return False
            
    def _execute_aave_strategy(self, strategy):
        """Execute Aave strategy"""
        try:
            amount = int(min(float(strategy['allocate_amount']), 10000))
            strategy_type = strategy['type']

            # Log debug info
            self.logger.info(f"Debug - Strategy details:")
            self.logger.info(f"- Amount: {amount}")
            self.logger.info(f"- Strategy type: {strategy_type}")
            self.logger.info(f"- Strategy value: {strategy_type.value}")

            # Execute the strategy directly
            try:
                # Use raw integer value for strategy type
                strategy_value = int(strategy_type.value)
                self.logger.info(f"Executing strategy with value: {strategy_value} and amount: {amount}")
                
                result = self.vault_manager.allocate_to_strategy(
                    strategy_value,  # Pass the raw integer value
                    amount
                )

                if result:
                    self.logger.info(f"Successfully executed strategy with amount: {amount}")
                    return True
                else:
                    self.logger.error("Strategy execution failed")
                    return False

            except Exception as e:
                self.logger.error(f"Error in allocate_to_strategy: {e}")
                return False

        except Exception as e:
            self.logger.error(f"Error executing Aave strategy: {e}")
            return False
            
    def _execute_sonic_strategy(self, strategy):
        """Execute Sonic strategy"""
        try:
            # Allocate to Sonic strategy
            self.vault_manager.allocate_to_strategy(
                StrategyType.STRATEGY_2,
                strategy['allocate_amount']
            )
            
            # Deposit to Sonic pool
            self.vault_manager.deposit_to_pool(
                'SONIC',
                strategy['deposit_amount']
            )
            
            self.logger.info(f"Successfully executed Sonic strategy with amount: {strategy['allocate_amount']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing Sonic strategy: {e}")
            return False

    def _analyze_aave_metrics(self, position):
        """Analyze AAVE-specific metrics"""
        return {
            'supply_apy': position['supply_apy'],
            'borrow_apy': position['borrow_apy'],
            'net_apy': position['estimated_net_apy'],
            'utilization_rate': position['utilization_rate'],
            'health_factor': position['health_factor']
        }
    
    def _analyze_protocol_metrics(self, protocol_metrics):
        """Analyze protocol-wide metrics for market insights"""
        return {
            'total_tvl': sum(p.metrics.tvl for p in protocol_metrics),
            'avg_volume_24h': sum(p.metrics.volume_24h or 0 for p in protocol_metrics) / len(protocol_metrics),
            'top_protocols': self.protocol_data.get_top_protocols_by_tvl(5),
            'highest_volume': self.protocol_data.get_highest_volume_24h()
        }
    
    def _assess_risk(self, positions):
        """Assess current risk levels for all strategies"""
        risk_assessment = {
            'overall_risk_level': 'low',
            'strategies': {}
        }
        
        # Assess AAVE_SONIC_BEEFY risk
        if 'aave_sonic' in positions:
            aave_position = positions['aave_sonic']
            aave_risk = 'low'
            
            if aave_position['health_factor'] < 1.5:
                aave_risk = 'high'
            elif aave_position['health_factor'] < 2.0:
                aave_risk = 'medium'
                
            risk_assessment['strategies']['AAVE_SONIC_BEEFY'] = {
                'risk_level': aave_risk,
                'health_factor': aave_position['health_factor'],
                'borrow_ratio': aave_position['borrow_ratio'],
                'suggested_adjustments': self._get_aave_risk_adjustments(aave_position)
            }
        
        # Assess SONIC_BEEFY_FARM risk
        if 'sonic_beefy' in positions:
            sonic_position = positions['sonic_beefy']
            sonic_risk = 'low'
            
            if sonic_position['validator_performance'] < 0.95:  # Below 95% performance
                sonic_risk = 'high'
            elif sonic_position['validator_performance'] < 0.98:  # Below 98% performance
                sonic_risk = 'medium'
                
            risk_assessment['strategies']['SONIC_BEEFY_FARM'] = {
                'risk_level': sonic_risk,
                'validator_performance': sonic_position['validator_performance'],
                'total_staked': sonic_position['total_staked'],
                'suggested_adjustments': self._get_sonic_risk_adjustments(sonic_position)
            }
        
        # Calculate overall risk level
        high_risk_count = sum(1 for s in risk_assessment['strategies'].values() if s['risk_level'] == 'high')
        if high_risk_count > 0:
            risk_assessment['overall_risk_level'] = 'high'
        elif any(s['risk_level'] == 'medium' for s in risk_assessment['strategies'].values()):
            risk_assessment['overall_risk_level'] = 'medium'
            
        return risk_assessment
    
    def _calculate_confidence_score(self, analysis):
        """Calculate confidence score for strategy recommendation"""
        score = 0.0
        
        # Factor in market trend
        if analysis['market_trend'].get('direction') == 'bullish':
            score += 0.3
        
        # Factor in risk assessment
        if analysis['risk_assessment']['risk_level'] == 'low':
            score += 0.3
        elif analysis['risk_assessment']['risk_level'] == 'medium':
            score += 0.15
            
        # Factor in historical patterns
        if analysis['historical_patterns'].get('similar_patterns_count', 0) > 5:
            score += 0.4
            
        return min(score, 1.0)

    def _analyze_market_trend(self):
        """Analyze market trends using historical data"""
        if len(self.historical_data) < 2:
            return "Insufficient historical data"
            
        # Calculate moving averages and trends
        recent_data = self.historical_data.tail(24)  # Last 24 data points
        aave_trend = recent_data['aave_apy'].diff().mean()
        
        return {
            'aave_trend': aave_trend,
            'market_direction': 'bullish' if aave_trend > 0 else 'bearish'
        }
    
    def _analyze_historical_patterns(self, similar_patterns):
        """Analyze similar historical patterns to inform decisions"""
        if not similar_patterns:
            return {"message": "No similar patterns found"}
            
        outcomes = []
        for pattern in similar_patterns:
            if pattern.get('outcome'):
                outcomes.append(pattern['outcome'])
                
        return {
            'similar_patterns_count': len(similar_patterns),
            'historical_outcomes': outcomes,
            'confidence_score': self._calculate_confidence(outcomes)
        }

    def _calculate_confidence(self, outcomes):
        """Calculate confidence score based on historical outcomes"""
        if not outcomes:
            return 0.0
            
        successful_outcomes = sum(1 for o in outcomes if o.get('success', False))
        return successful_outcomes / len(outcomes)

    def _get_aave_risk_adjustments(self, position):
        adjustments = []
        
        if position['health_factor'] < 1.5:
            adjustments.append("Reduce borrowed amount")
        if position['estimated_net_apy'] < 0:
            adjustments.append("Consider closing positions")
        
        return adjustments
    
    def _get_sonic_risk_adjustments(self, position):
        adjustments = []
        
        if position['validator_performance'] < 0.95:
            adjustments.append("Consider reducing stake")
        
        return adjustments
    
    def get_recommendation(self):
        """Get final recommendation based on all analyses"""
        analysis = self.analyze_market_conditions()
        risk = analysis['risk_assessment']
        historical = analysis['historical_patterns']
        
        recommendations = []
        
        # Risk-based recommendations
        if risk['risk_level'] == 'high':
            recommendations.extend(risk['strategies']['AAVE_SONIC_BEEFY']['suggested_adjustments'])
            recommendations.extend(risk['strategies']['SONIC_BEEFY_FARM']['suggested_adjustments'])
            
        # Market trend-based recommendations
        trend = analysis['market_trend']
        if trend.get('market_direction') == 'bullish':
            recommendations.append("Consider increasing positions")
        elif trend.get('market_direction') == 'bearish':
            recommendations.append("Consider reducing exposure")
            
        recommendation_data = {
            'recommendations': recommendations,
            'analysis': analysis,
            'timestamp': pd.Timestamp.now()
        }
        
        # Record strategy recommendation
        self.knowledge.record_strategy_outcome(
            strategy=recommendations,
            outcome={'pending': True}
        )
        
        return recommendation_data

    async def analyze_strategies(self):
        """Analyze both strategies and return recommendations"""
        try:
            # Get current allocations
            strategy1_allocation = self.vault_manager.get_pool_balance(
                StrategyType.STRATEGY_1.value,
                self.aave.get_lending_token_address()
            )
            
            strategy2_allocation = self.vault_manager.get_pool_balance(
                StrategyType.STRATEGY_2.value,
                self.config['contracts']['sonic']['wrapped_sonic']
            )
            
            total_assets = self.vault_manager.get_total_assets()
            
            # Analyze Strategy 1 (AaveSonicBeefy)
            strategy1_data = self.aave.get_optimal_position()
            strategy1_apy = strategy1_data['estimated_net_apy']
            
            # Analyze Strategy 2 (SonicBeefyFarm)
            strategy2_data = self.market_data.get_sonic_beefy_data()
            strategy2_apy = strategy2_data['farm_apy']
            
            recommendations = []
            
            # Check if rebalance needed for Strategy 1
            if strategy1_apy > self.config['strategy']['min_apy']:
                current_percentage = strategy1_allocation / total_assets
                target_percentage = self._calculate_target_allocation(strategy1_data)
                
                if abs(current_percentage - target_percentage) > self.config['strategy']['rebalance_threshold']:
                    recommendations.append({
                        'type': StrategyType.STRATEGY_1,
                        'action': 'increase_allocation' if target_percentage > current_percentage else 'decrease_allocation',
                        'amount': abs(total_assets * target_percentage - strategy1_allocation),
                        'apy': strategy1_apy
                    })
            
            # Check if rebalance needed for Strategy 2
            if strategy2_apy > self.config['strategy']['min_apy']:
                current_percentage = strategy2_allocation / total_assets
                target_percentage = self._calculate_target_allocation(strategy2_data)
                
                if abs(current_percentage - target_percentage) > self.config['strategy']['rebalance_threshold']:
                    recommendations.append({
                        'type': StrategyType.STRATEGY_2,
                        'action': 'increase_allocation' if target_percentage > current_percentage else 'decrease_allocation',
                        'amount': abs(total_assets * target_percentage - strategy2_allocation),
                        'apy': strategy2_apy
                    })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error analyzing strategies: {e}")
            return []

    def _validate_strategy(self, strategy):
        """Validate strategy parameters before execution"""
        try:
            required_fields = ['action', 'amount']
            if not all(field in strategy for field in required_fields):
                return False
                
            if strategy['amount'] <= 0:
                return False
                
            # Check against vault limits
            total_assets = self.vault_manager.get_total_assets()
            if strategy['amount'] > total_assets * self.config['strategy']['max_allocation_percentage']:
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Strategy validation error: {e}")
            return False 

    async def check_rebalance_needed(self):
        """Check if rebalancing is needed"""
        try:
            market_data = await self.analyze_market_conditions()
            current_allocation = self.vault_manager.get_pool_balance(
                StrategyType.AAVE.value,
                self.aave.LENDING_TOKEN
            )
            total_assets = self.vault_manager.get_total_assets()
            
            if total_assets == 0:
                self.logger.info("No assets in vault, no rebalance needed")
                return None
            
            # Check allocation percentage
            current_percentage = current_allocation / total_assets
            target_percentage = market_data['optimal_allocation'] / total_assets if total_assets > 0 else 0
            
            self.logger.info(f"Current allocation: {current_percentage:.2%}")
            self.logger.info(f"Target allocation: {target_percentage:.2%}")
            
            if abs(current_percentage - target_percentage) > self.config['strategy']['rebalance_threshold']:
                new_amount = total_assets * target_percentage
                return {
                    'action': 'increase_allocation' if new_amount > current_allocation else 'decrease_allocation',
                    'amount': abs(new_amount - current_allocation)
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Rebalance check error: {e}")
            return None

    async def check_emergency_conditions(self):
        """Check for emergency conditions requiring immediate action"""
        try:
            emergency_actions = []
            
            # Check Strategy 1 (AaveSonicBeefy) health
            strategy1_data = self.aave.get_optimal_position()
            if strategy1_data['health_factor'] < self.config['strategy']['emergency_health_factor']:
                emergency_actions.append({
                    'type': StrategyType.STRATEGY_1,
                    'action': 'decrease_allocation',
                    'amount': self.vault_manager.get_pool_balance(
                        StrategyType.STRATEGY_1.value,
                        self.aave.get_lending_token_address()
                    ) * self.config['strategy']['emergency_withdrawal_percentage']
                })
            
            # Check Strategy 2 (SonicBeefyFarm) validator performance
            strategy2_data = self.market_data.get_sonic_beefy_data()
            if strategy2_data['validator_performance'] < self.config['strategy']['min_validator_performance']:
                emergency_actions.append({
                    'type': StrategyType.STRATEGY_2,
                    'action': 'decrease_allocation',
                    'amount': self.vault_manager.get_pool_balance(
                        StrategyType.STRATEGY_2.value,
                        self.config['contracts']['sonic']['wrapped_sonic']
                    ) * self.config['strategy']['emergency_withdrawal_percentage']
                })
            
            return emergency_actions if emergency_actions else None
            
        except Exception as e:
            self.logger.error(f"Emergency check error: {e}")
            return None 

    async def optimize_allocation(self):
        """Main optimization function that creates complex strategies"""
        try:
            market_data = await self.analyze_market_conditions()
            
            # Create a complex strategy that might use all three functions
            strategy = {
                'type': StrategyType.STRATEGY_1,
                'allocate_amount': self._calculate_optimal_allocation(market_data),
                'deposit_pool': 'AAVE',
                'deposit_amount': self._calculate_pool_deposit(market_data),
                'custom_function': {
                    'target': self.STRATEGY_1,
                    'signature': 'updateBorrowRatio(uint256)',
                    'args': [{
                        'type': 'uint256',
                        'value': self._calculate_optimal_borrow_ratio(market_data)
                    }]
                }
            }

            return await self.execute_strategy(strategy)

        except Exception as e:
            self.logger.error(f"Error in optimization: {e}")
            return False

    async def rebalance_if_needed(self):
        """Check and rebalance strategies if needed"""
        try:
            current_data = await self.analyze_market_conditions()
            
            if self._needs_rebalancing(current_data):
                strategy = {
                    'type': StrategyType.STRATEGY_1,
                    'allocate_amount': current_data['optimal_allocation'],
                    'custom_function': {
                        'target': self.STRATEGY_1,
                        'signature': 'rebalance()',
                        'args': []
                    }
                }
                
                return self.execute_strategy(strategy)
                
            return False

        except Exception as e:
            self.logger.error(f"Error in rebalancing check: {e}")
            return False 

    def _calculate_optimal_allocation(self, market_data):
        """Calculate optimal allocation based on market data"""
        try:
            # Get current total assets
            total_assets = self.vault_manager.get_total_assets()
            if total_assets == 0:
                self.logger.warning("No assets available for allocation")
                return 0
                
            # Calculate based on APY with sanity checks
            aave_apy = market_data.get('aave_apy', 0)
            sonic_apy = market_data.get('sonic_apy', 0)
            
            # Add sanity checks for APY values
            MAX_REASONABLE_APY = 100  # 100% APY as maximum reasonable value
            if aave_apy > MAX_REASONABLE_APY:
                self.logger.warning(f"Unreasonable AAVE APY detected: {aave_apy}%, capping at {MAX_REASONABLE_APY}%")
                aave_apy = MAX_REASONABLE_APY
            if sonic_apy > MAX_REASONABLE_APY:
                self.logger.warning(f"Unreasonable Sonic APY detected: {sonic_apy}%, capping at {MAX_REASONABLE_APY}%")
                sonic_apy = MAX_REASONABLE_APY
            
            # Get max allocation with a more conservative limit
            max_allocation = min(total_assets * self.config['strategy']['max_allocation_percentage'], 10000)  # Cap at 10000
            
            # Choose best APY
            best_apy = max(aave_apy, sonic_apy)
            
            if best_apy > self.config['strategy']['min_apy']:
                # Start with a small test amount
                test_amount = min(1000, max_allocation)  # Start with 1000 or less
                self.logger.info(f"Starting with test allocation: {test_amount} (Best APY: {best_apy}%)")
                return test_amount
                
            self.logger.info(f"APY too low for allocation. Best APY: {best_apy}%")
            return 0
            
        except Exception as e:
            self.logger.error(f"Error calculating optimal allocation: {e}")
            return 0

    def _needs_rebalancing(self, current_data):
        """Check if rebalancing is needed"""
        try:
            current_allocation = self.vault_manager.get_total_assets()
            target_allocation = current_data['optimal_allocation']
            
            return abs(current_allocation - target_allocation) > self.config['strategy']['rebalance_threshold']
        except Exception as e:
            self.logger.error(f"Error checking rebalance need: {e}")
            return False 

    async def get_ai_recommendation(self, market_data):
        """Get AI-powered strategy recommendations"""
        try:
            if not os.getenv('OPENAI_API_KEY'):
                self.logger.warning("OpenAI API key not set. Skipping AI recommendation.")
                return None

            # Prepare context for the AI
            context = {
                "market_metrics": {
                    "aave_apy": market_data['metrics']['aave_apy'],
                    "sonic_apy": market_data['metrics']['sonic_apy'],
                    "health_factor": market_data['metrics']['health_factor'],
                    "utilization": market_data['metrics']['utilization']
                },
                "current_allocation": self.vault_manager.get_total_assets(),
                "risk_assessment": self._assess_risk(market_data),
                "market_trend": self._analyze_market_trend()
            }

            # Create prompt for the AI
            prompt = f"""
            As a DeFi strategy advisor, analyze the following market conditions and recommend an optimal strategy:

            Market Metrics:
            - AAVE APY: {context['market_metrics']['aave_apy']}%
            - Sonic APY: {context['market_metrics']['sonic_apy']}%
            - Health Factor: {context['market_metrics']['health_factor']}
            - Utilization: {context['market_metrics']['utilization']}%

            Current Total Allocation: {context['current_allocation']}
            Market Trend: {context['market_trend']['market_direction']}
            Risk Level: {context['risk_assessment']['overall_risk_level']}

            Provide a strategy recommendation including:
            1. Recommended strategy type (AAVE, STRATEGY_1, or STRATEGY_2)
            2. Allocation amount
            3. Risk assessment
            4. Reasoning for the recommendation
            """

            # Get AI response
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a DeFi strategy advisor specialized in yield optimization."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            # Parse AI response
            recommendation = response.choices[0].message.content

            # Log the AI recommendation
            self.logger.info(f"AI Strategy Recommendation: {recommendation}")

            # Record the recommendation in knowledge box
            self.knowledge.record_strategy_outcome(
                strategy={"ai_recommendation": recommendation},
                outcome={"pending": True}
            )

            return recommendation

        except Exception as e:
            self.logger.error(f"Error getting AI recommendation: {e}")
            return None

    async def execute_optimal_strategy(self):
        """Execute the optimal strategy based on market conditions and AI recommendations"""
        try:
            market_data = await self.analyze_market_conditions()
            
            # Get AI recommendation
            ai_recommendation = await self.get_ai_recommendation(market_data)
            
            if ai_recommendation:
                self.logger.info("Using AI-powered strategy recommendation")
                try:
                    # Parse AI recommendation into strategy format
                    strategy = self._parse_ai_recommendation(ai_recommendation)
                    if strategy:
                        self.logger.info(f"Executing AI recommended strategy: {strategy}")
                        return await self.execute_strategy(strategy)
                except Exception as e:
                    self.logger.error(f"Failed to execute AI strategy: {e}")
                    # Fall through to traditional strategy
            
            # Fallback to traditional strategy logic
            self.logger.info("Using traditional strategy logic")
            total_assets = self.vault_manager.get_total_assets()
            
            if market_data['metrics']['aave_apy'] > self.config['strategy']['min_apy']:
                optimal_amount = self._calculate_optimal_allocation(market_data)
                # strategy = {
                #     'type': StrategyType.AAVE,
                #     'allocate_amount': optimal_amount,
                #     'deposit_pool': 'AAVE',
                #     'deposit_amount': optimal_amount
                # }
                test_amount = 1000  # Start small
                strategy = {
                    'type': StrategyType.STRATEGY_1,
                    'allocate_amount': test_amount,
                    'deposit_pool': 'AAVE',
                    'deposit_amount': test_amount
                }
                return await self.execute_strategy(strategy)
                
            elif market_data['metrics']['sonic_apy'] > self.config['strategy']['min_apy']:
                optimal_amount = self._calculate_optimal_allocation(market_data)
                strategy = {
                    'type': StrategyType.STRATEGY_2,
                    'allocate_amount': optimal_amount,
                    'deposit_pool': 'SONIC',
                    'deposit_amount': optimal_amount
                }
                return await self.execute_strategy(strategy)
            
            self.logger.info("No profitable strategies found")
            return False

        except Exception as e:
            self.logger.error(f"Error executing optimal strategy: {e}")
            return False

    def _parse_ai_recommendation(self, ai_recommendation: str) -> dict:
        """Parse AI recommendation text into a structured strategy"""
        try:
            # Look for key strategy components in the AI's response
            strategy_type = None
            amount = None
            
            # Parse strategy type
            if "AAVE" in ai_recommendation:
                strategy_type = StrategyType.AAVE
            elif "STRATEGY_1" in ai_recommendation:
                strategy_type = StrategyType.STRATEGY_1
            elif "STRATEGY_2" in ai_recommendation:
                strategy_type = StrategyType.STRATEGY_2
            
            # Look for amount in the recommendation
            # This is a simple example; you might want to make this more sophisticated
            import re
            amount_match = re.search(r'amount[:\s]+(\d+)', ai_recommendation.lower())
            if amount_match:
                amount = int(amount_match.group(1))
            
            if strategy_type and amount:
                strategy = {
                    'type': strategy_type,
                    'allocate_amount': amount,
                    'deposit_pool': 'AAVE' if strategy_type in [StrategyType.AAVE, StrategyType.STRATEGY_1] else 'SONIC',
                    'deposit_amount': amount
                }
                self.logger.info(f"Successfully parsed AI recommendation into strategy: {strategy}")
                return strategy
            
            self.logger.warning("Could not parse complete strategy from AI recommendation")
            return None
            
        except Exception as e:
            self.logger.error(f"Error parsing AI recommendation: {e}")
            return None 