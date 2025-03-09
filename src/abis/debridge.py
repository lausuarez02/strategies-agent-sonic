DEBRIDGE_PROXY_ABI = [
    {
        "inputs": [],
        "name": "implementation",
        "outputs": [{"internalType": "address", "name": "implementation_", "type": "address"}],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

DEBRIDGE_IMPLEMENTATION_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "token", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
            {"internalType": "uint256", "name": "chainIdTo", "type": "uint256"},
            {"internalType": "bytes32", "name": "receiver", "type": "bytes32"},
            {"internalType": "bytes", "name": "permit", "type": "bytes"},
            {"internalType": "bool", "name": "useAssetFee", "type": "bool"},
            {"internalType": "uint32", "name": "referralCode", "type": "uint32"},
            {"internalType": "bytes", "name": "autoParams", "type": "bytes"}
        ],
        "name": "send",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "chainIdTo", "type": "uint256"},
            {"internalType": "bytes32", "name": "receiver", "type": "bytes32"},
            {"internalType": "bytes", "name": "permit", "type": "bytes"},
            {"internalType": "bool", "name": "useAssetFee", "type": "bool"},
            {"internalType": "uint32", "name": "referralCode", "type": "uint32"},
            {"internalType": "bytes", "name": "autoParams", "type": "bytes"}
        ],
        "name": "sendNative",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "payable",
        "type": "function"
    }
] 