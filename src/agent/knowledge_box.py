import pandas as pd
from datetime import datetime, timedelta
import json
import os
import logging
from typing import Dict, List

class KnowledgeBox:
    def __init__(self, storage_path="data/knowledge"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # Initialize different knowledge categories
        self.categories = {
            'market_patterns': self._load_knowledge('market_patterns.json'),
            'yield_patterns': self._load_knowledge('yield_patterns.json'),
            'risk_events': self._load_knowledge('risk_events.json'),
            'strategy_outcomes': self._load_knowledge('strategy_outcomes.json')
        }
        self.logger = logging.getLogger('KnowledgeBox')
        self.market_patterns = []
        self.strategy_outcomes = []

    def _load_knowledge(self, filename):
        """Load knowledge from storage"""
        try:
            with open(f"{self.storage_path}/{filename}", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def _save_knowledge(self, category, data):
        """Save knowledge to storage"""
        filename = f"{category}.json"
        with open(f"{self.storage_path}/{filename}", 'w') as f:
            json.dump(data, f, indent=2)

    def add_market_pattern(self, pattern: Dict):
        """Add a new market pattern to the knowledge base"""
        try:
            self.market_patterns.append({
                'timestamp': pd.Timestamp.now(),
                'data': pattern
            })
        except Exception as e:
            self.logger.error(f"Error adding market pattern: {e}")

    def add_yield_pattern(self, pattern):
        """Record yield pattern observation"""
        self.categories['yield_patterns'].append({
            'timestamp': datetime.now().isoformat(),
            'pattern': pattern,
            'result': None
        })
        self._save_knowledge('yield_patterns', self.categories['yield_patterns'])

    def record_risk_event(self, event):
        """Record risk-related events"""
        self.categories['risk_events'].append({
            'timestamp': datetime.now().isoformat(),
            'event': event,
            'impact': None
        })
        self._save_knowledge('risk_events', self.categories['risk_events'])

    def record_strategy_outcome(self, strategy, outcome):
        """Record the outcome of a strategy decision"""
        self.categories['strategy_outcomes'].append({
            'timestamp': datetime.now().isoformat(),
            'strategy': strategy,
            'outcome': outcome
        })
        self._save_knowledge('strategy_outcomes', self.categories['strategy_outcomes'])

    def find_similar_patterns(self, current_data, category='market_patterns', lookback_days=30):
        """Find similar historical patterns"""
        patterns = self.categories[category]
        lookback_date = datetime.now() - timedelta(days=lookback_days)
        
        recent_patterns = [
            p for p in patterns 
            if datetime.fromisoformat(p['timestamp']) > lookback_date
        ]
        
        # Implement pattern matching logic here
        similar_patterns = []
        for pattern in recent_patterns:
            similarity_score = self._calculate_similarity(current_data, pattern['pattern'])
            if similarity_score > 0.8:  # 80% similarity threshold
                similar_patterns.append(pattern)
                
        return similar_patterns

    def _calculate_similarity(self, pattern1, pattern2):
        """Calculate similarity between two patterns"""
        # Mock implementation - replace with actual similarity calculation
        return 0.9  # Example similarity score 

    def get_recent_patterns(self, n: int = 10) -> List[Dict]:
        """Get n most recent patterns"""
        try:
            return self.market_patterns[-n:]
        except Exception as e:
            self.logger.error(f"Error getting recent patterns: {e}")
            return [] 