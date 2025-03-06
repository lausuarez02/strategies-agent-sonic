# Cult of Ronin: Off-Chain Execution & Automation Repo (strategies-agent)

This repository handles all off-chain logic and automation for decentralized finance (DeFi) strategies. Written in Python, it integrates with Web3 to execute various tasks such as monitoring rewards, automated execution, data fetching, and smart contract interaction.

## Overview

The core functionalities of this repo include:
- Intelligent agent-based market analysis and strategy recommendations
- Monitoring rewards and Annual Percentage Yields (APY)
- Automated arbitrage execution across protocols
- Data aggregation from multiple DeFi protocols (Aave, Sonic)
- Smart contract interaction through Web3

## Folder Structure

```plaintext
📂 strategies-agent/
├── 📂 src/
│   ├── 📂 agent/
│   │   ├── smart_agent.py         # Main agent logic
│   │   ├── knowledge_box.py       # Historical pattern analysis
│   ├── 📂 data_providers/
│   │   ├── aave_provider.py       # Aave protocol data
│   │   ├── sonic_provider.py      # Sonic protocol data
│   │   ├── market_data.py         # Market data aggregation
│   ├── 📂 scripts/
│   │   ├── arbitrage_manager.py   # Arbitrage execution logic
│   ├── main.py                    # Main orchestration logic
├── 📂 configs/
│   ├── config.yaml               # Configuration settings
├── 📂 data/
│   ├── 📂 knowledge/
│   │   ├── market_patterns.json   # Historical market patterns
│   │   ├── yield_patterns.json    # Yield strategy patterns
│   │   ├── risk_events.json       # Risk-related events
│   │   ├── strategy_outcomes.json # Strategy outcomes
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
```

## Components

### Smart Agent System

The smart agent system analyzes market conditions and provides strategic recommendations:

- **Market Analysis**: Monitors trends, yields, and risk factors
- **Pattern Recognition**: Identifies similar historical market conditions
- **Strategy Recommendations**: Provides data-driven strategy suggestions
- **Risk Assessment**: Evaluates current market risks and positions

### Data Providers

Multiple data providers feed information to the smart agent:

- **Aave Provider**: Fetches lending/borrowing rates, positions, and rewards
- **Sonic Provider**: Monitors farming opportunities and yields
- **Market Data Aggregator**: Combines data from multiple sources

### Knowledge Box System

The agent implements a knowledge box system that stores and analyzes historical patterns and outcomes to improve decision-making over time. This system includes:

#### Components

- **Market Patterns**: Records and analyzes recurring market conditions and their outcomes
- **Yield Patterns**: Tracks yield strategy performance and patterns
- **Risk Events**: Documents risk-related events and their impacts
- **Strategy Outcomes**: Records the success/failure of previous recommendations

#### Storage Structure

```plaintext
📂 data/
├── 📂 knowledge/
│   ├── market_patterns.json    # Historical market pattern data
│   ├── yield_patterns.json     # Yield strategy patterns
│   ├── risk_events.json        # Risk-related events
│   ├── strategy_outcomes.json  # Historical strategy outcomes
```

#### Features

- Pattern Recognition: Identifies similar historical market conditions
- Outcome Analysis: Learns from previous strategy successes and failures
- Confidence Scoring: Calculates confidence levels for recommendations
- Adaptive Learning: Improves decision-making based on historical data

### Arbitrage System

Independent arbitrage monitoring and execution:

- **Opportunity Detection**: Monitors price differences across protocols
- **Profitability Analysis**: Calculates potential profits including fees
- **Automated Execution**: Executes trades when profitable opportunities arise

## Configuration

Configure the system through `config.yaml`:

```yaml
networks:
  sonic:
    rpc_url: "https://rpc.soniclabs.com"
    chain_id: 146
  arbitrum:
    rpc_url: "https://arbitrum-mainnet.infura.io/v3/${ARB_RPC_KEY}"
    chain_id: 42161

contracts:
  sonic:
    sonic_vault: "0xa3c0..."
    sonic_oracle: "0xE68e..."
  arbitrum:
    aave:
      pool: "0x794a..."
      pool_data_provider: "0x69FA..."

strategy:
  reinvest_threshold: 0.05
  rebalance_interval: 86400
  arbitrage:
    min_profit_percentage: 0.02
    vault_percentage: 0.05
```

## Installation

```bash
git clone https://github.com/lausuarez02/strategies-agent-sonic.git
cd strategies-agent-sonic
pip install -r requirements.txt
```

## Usage

Run the main orchestrator:

```bash
python src/main.py
```

This will start:
- The smart agent's market analysis and recommendation system
- Independent arbitrage monitoring
- Data collection from all providers

## Dependencies

Key dependencies include:
- `web3.py`: For Ethereum smart contract interaction
- `pandas`: For data analysis and pattern recognition
- `pyyaml`: For configuration management

## Contributing

Feel free to fork this repository and submit pull requests. If you find a bug or want to suggest a feature, open an issue.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.