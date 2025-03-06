from typing import Dict, List
from .base_protocol import BaseProtocolProvider, ProtocolData
from .sonic_protocols import (
    SiloFinanceProvider,
    BeetsProvider,
    ShadowExchangeProvider,
    OriginSonicProvider
)

class ProtocolDataAggregator:
    def __init__(self, web3_instance):
        # Initialize all protocol providers
        self.providers: Dict[str, BaseProtocolProvider] = {
            "silo": SiloFinanceProvider(web3_instance),
            "beets": BeetsProvider(web3_instance),
            "shadow": ShadowExchangeProvider(web3_instance),
            "origin_sonic": OriginSonicProvider(web3_instance)
        }
    
    def get_all_protocols_data(self) -> List[ProtocolData]:
        """Get data from all protocols"""
        return [
            provider.get_protocol_info()
            for provider in self.providers.values()
        ]
    
    def get_total_tvl(self) -> float:
        """Get total TVL across all protocols"""
        return sum(
            protocol.metrics.tvl
            for protocol in self.get_all_protocols_data()
        )
    
    def get_protocols_by_category(self, category) -> List[ProtocolData]:
        """Get all protocols in a specific category"""
        return [
            protocol for protocol in self.get_all_protocols_data()
            if protocol.category == category
        ]
    
    def get_top_protocols_by_tvl(self, limit: int = 5) -> List[ProtocolData]:
        """Get top protocols by TVL"""
        protocols = self.get_all_protocols_data()
        return sorted(
            protocols,
            key=lambda x: x.metrics.tvl,
            reverse=True
        )[:limit]
    
    def get_highest_volume_24h(self) -> ProtocolData:
        """Get protocol with highest 24h volume"""
        protocols = [p for p in self.get_all_protocols_data() if p.metrics.volume_24h is not None]
        return max(protocols, key=lambda x: x.metrics.volume_24h) 