
# Cult of Ronin: Off-Chain Execution & Automation Repo (strategies-agent)

This repository handles all off-chain logic and automation for decentralized finance (DeFi) strategies. Written in Python (or your preferred language), it integrates with Web3 to execute various tasks such as monitoring rewards, automated execution, data fetching, and smart contract interaction.

## Overview

The core functionalities of this repo include:
- Monitoring rewards and Annual Percentage Yields (APY).
- Automating execution tasks such as compounding, rebalancing, and bridging.
- Fetching and analyzing data from oracle feeds, APR trends, and more.
- Interacting with smart contracts through libraries like Web3.py or Ethers.js.

## Folder Structure

```plaintext
📂 strategies-agent/
├── 📂 scripts/
│ ├── monitor_rewards.py      # Fetches APY, monitors rewards & triggers reinvestment
│ ├── auto_compound.py        # Executes reinvestment when threshold met
│ ├── borrow_and_farm.py      # Handles cross-chain borrowing & farming process
├── 📂 configs/
│ ├── config.yaml            # Stores addresses, thresholds, etc.
├── 📂 web3/
│ ├── debridge.py            # Handles deBridge cross-chain transactions
│ ├── sonic.py               # Interacts with Sonic staking/farming contracts
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
```

### `scripts/`

- **monitor_rewards.py**: This script fetches the current APY (Annual Percentage Yield), monitors rewards, and triggers reinvestment when thresholds are met.
- **auto_compound.py**: Automatically compounds rewards when a predefined threshold is reached, ensuring optimal returns.
- **borrow_and_farm.py**: Handles cross-chain borrowing and farming operations, enabling the user to take advantage of farming opportunities on multiple blockchains.

### `configs/`

- **config.yaml**: Stores configuration values such as smart contract addresses, thresholds for reinvestment, and other parameters used across scripts.

### `web3/`

- **debridge.py**: Manages cross-chain transactions using the deBridge protocol to transfer assets between different blockchains.
- **sonic.py**: Interacts with Sonic's staking and farming smart contracts for yield generation and farming strategies.

## Installation

Clone this repository and install dependencies using the following commands:

```bash
git clone https://github.com/lausuarez02/strategies-agent-sonic.git
cd strategies-agent-sonic
pip install -r requirements.txt
```

## Configuration

1. **config.yaml**: Make sure to configure all necessary parameters like contract addresses, thresholds for automation, and other custom settings.
   
Example `config.yaml`:

```yaml
addresses:
  compound_contract: "0x12345...abcde"
  staking_contract: "0x67890...fghij"
thresholds:
  reinvestment: 1000
  borrowing: 5000
```

## Usage

Each script can be run individually depending on your automation needs.

### Monitoring Rewards

To monitor rewards and APY, run:

```bash
python scripts/monitor_rewards.py
```

This will fetch the current APY and rewards, and trigger reinvestment when the set thresholds are reached.

### Auto Compounding

To start auto-compounding rewards when a threshold is met:

```bash
python scripts/auto_compound.py
```

This script will automatically reinvest rewards once the value reaches the configured threshold.

### Borrowing and Farming

To execute the borrowing and farming strategy:

```bash
python scripts/borrow_and_farm.py
```

This will handle cross-chain borrowing and farming processes based on the defined logic.

## Dependencies

Make sure to install all required libraries:

```bash
pip install -r requirements.txt
```

Key dependencies include:
- `web3.py`: For Ethereum smart contract interaction.
- `requests`: For API calls and data fetching.
- `yaml`: For reading configuration files.

## Contributing

Feel free to fork this repository and submit pull requests. If you find a bug or want to suggest a feature, open an issue, and I'll review it.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
