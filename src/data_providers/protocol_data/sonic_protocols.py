from .base_protocol import BaseProtocolProvider, ProtocolMetrics, ProtocolData, ProtocolCategory
from web3 import Web3
import yaml

class SiloFinanceProvider(BaseProtocolProvider):
    def __init__(self, web3_instance: Web3):
        self.web3 = web3_instance
        with open("configs/config.yaml", "r") as f:
            self.config = yaml.safe_load(f)
            
    def get_protocol_metrics(self) -> ProtocolMetrics:
        # Implement Silo-specific metrics collection
        return ProtocolMetrics(
            tvl=187.62e6,  # Example values
            tvl_change_24h=16.07,
            volume_24h=None,
            volume_change_24h=71.23
        )
    
    def get_protocol_info(self) -> ProtocolData:
        return ProtocolData(
            name="Silo Finance",
            category=ProtocolCategory.LENDING,
            chain_count=5,
            chains=["Sonic", "Ethereum", "Arbitrum", "Base", "Optimism"],
            metrics=self.get_protocol_metrics()
        )

class BeetsProvider(BaseProtocolProvider):
    def __init__(self, web3_instance: Web3):
        self.web3 = web3_instance
        with open("configs/config.yaml", "r") as f:
            self.config = yaml.safe_load(f)
    
    def get_protocol_metrics(self) -> ProtocolMetrics:
        return ProtocolMetrics(
            tvl=167e6,
            tvl_change_24h=29.47,
            volume_24h=8.51e6,
            volume_change_24h=117.0,
            fees_24h=7815,
            revenue_24h=1954
        )
    
    def get_protocol_info(self) -> ProtocolData:
        return ProtocolData(
            name="Beets",
            category=ProtocolCategory.DEX,
            chain_count=3,
            chains=["Sonic", "Fantom", "Optimism"],
            metrics=self.get_protocol_metrics()
        )

class ShadowExchangeProvider(BaseProtocolProvider):
    # Similar implementation for Shadow Exchange
    pass

class OriginSonicProvider(BaseProtocolProvider):
    def __init__(self, web3_instance: Web3):
        self.web3 = web3_instance
        with open("configs/config.yaml", "r") as f:
            self.config = yaml.safe_load(f)
    
    def get_protocol_metrics(self) -> ProtocolMetrics:
        return ProtocolMetrics(
            tvl=33.9e6,
            tvl_change_24h=12.96,
            volume_change_24h=1334.0
        )
    
    def get_protocol_info(self) -> ProtocolData:
        return ProtocolData(
            name="Origin Sonic",
            category=ProtocolCategory.LIQUID_STAKING,
            chain_count=1,
            chains=["Sonic"],
            metrics=self.get_protocol_metrics()
        ) 