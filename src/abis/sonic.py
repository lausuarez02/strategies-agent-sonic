SONIC_VAULT_ABI = [
    {
        "inputs": [{"type": "uint256"}],
        "name": "deposit",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getAssetPrice",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

SONIC_ORACLE_ABI = [
    {
        "inputs": [{"type": "string"}],
        "name": "getAssetPrice",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

SONIC_ZAPPER_ABI = [
    {
        "inputs": [{"type": "uint256"}],
        "name": "zapIn",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
] 