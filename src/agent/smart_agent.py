from ..data_providers.market_data import MarketDataAggregator
from ..data_providers.aave_provider import AaveDataProvider
from ..data_providers.sonic_provider import SonicDataProvider
from ..data_providers.protocol_data.aggregator import ProtocolDataAggregator
import pandas as pd
import logging
from .knowledge_box import KnowledgeBox

class SmartAgent:
    def __init__(self, arb_web3, sonic_web3):
        self.logger = logging.getLogger('SmartAgent')
        
        # Initialize data providers
        self.market_data = MarketDataAggregator(arb_web3, sonic_web3)
        self.aave = AaveDataProvider(arb_web3)
        self.sonic = SonicDataProvider(sonic_web3)
        self.protocol_data = ProtocolDataAggregator(sonic_web3)
        
        # Initialize historical data storage
        self.historical_data = pd.DataFrame()
        
        # Initialize knowledge box
        self.knowledge = KnowledgeBox()
        
    def analyze_market_conditions(self):
        """Analyze current market conditions and return insights"""
        current_data = self.market_data.get_market_data()
        self.historical_data = pd.concat([self.historical_data, current_data])
        
        # Get detailed position data from Aave
        aave_position = self.aave.get_optimal_position()
        
        # Find similar historical patterns
        similar_patterns = self.knowledge.find_similar_patterns(current_data)
        
        analysis = {
            'market_trend': self._analyze_market_trend(),
            'yield_comparison': self._compare_yields(),
            'risk_assessment': self._assess_risk(aave_position),
            'historical_patterns': self._analyze_historical_patterns(similar_patterns),
            'recommended_actions': [],
            'protocol_metrics': {
                'total_tvl': self.protocol_data.get_total_tvl(),
                'top_protocols': self.protocol_data.get_top_protocols_by_tvl(5),
                'highest_volume': self.protocol_data.get_highest_volume_24h()
            }
        }
        
        # Record new pattern
        self.knowledge.add_market_pattern({
            'market_data': current_data.to_dict(),
            'analysis': analysis
        })
        
        return analysis
    
    def _analyze_market_trend(self):
        """Analyze market trends using historical data"""
        if len(self.historical_data) < 2:
            return "Insufficient historical data"
            
        # Calculate moving averages and trends
        recent_data = self.historical_data.tail(24)  # Last 24 data points
        aave_trend = recent_data['aave_apy'].diff().mean()
        sonic_trend = recent_data['sonic_apy'].diff().mean()
        
        return {
            'aave_trend': aave_trend,
            'sonic_trend': sonic_trend,
            'market_direction': 'bullish' if aave_trend + sonic_trend > 0 else 'bearish'
        }
    
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
    
    def get_recommendation(self):
        """Get final recommendation based on all analyses"""
        analysis = self.analyze_market_conditions()
        yields = self._compare_yields()
        risk = analysis['risk_assessment']
        historical = analysis['historical_patterns']
        
        recommendations = []
        
        # Historical pattern-based recommendations
        if historical.get('confidence_score', 0) > 0.8:
            recommendations.append("High confidence based on historical patterns")
        
        # Yield-based recommendations
        if yields['yield_diff'] > 0.02:  # 2% threshold
            recommendations.append(f"Move funds to {yields['recommended_protocol']} for better yields")
            
        # Risk-based recommendations
        if risk['risk_level'] == 'high':
            recommendations.extend(risk['suggested_adjustments'])
            
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