from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

class ProtocolCategory(Enum):
    LENDING = "Lending"
    DEX = "Dexs"
    CDP = "CDP"
    LIQUIDITY_MANAGER = "Liquidity manager"
    LIQUID_STAKING = "Liquid Staking"

@dataclass
class ProtocolMetrics:
    tvl: float
    tvl_change_24h: float
    volume_24h: Optional[float] = None
    volume_change_24h: Optional[float] = None
    fees_24h: Optional[float] = None
    revenue_24h: Optional[float] = None
    
@dataclass
class ProtocolData:
    name: str
    category: ProtocolCategory
    chain_count: int
    chains: List[str]
    metrics: ProtocolMetrics

class BaseProtocolProvider(ABC):
    @abstractmethod
    def get_protocol_metrics(self) -> ProtocolMetrics:
        """Get current protocol metrics"""
        pass
    
    @abstractmethod
    def get_protocol_info(self) -> ProtocolData:
        """Get general protocol information"""
        pass 