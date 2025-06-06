import requests

def get_solana_transaction(tx_hash):
    url = "https://api.mainnet-beta.solana.com"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            tx_hash,
            {
                "encoding": "json",
                "maxSupportedTransactionVersion": 0
            }
        ]
    }
    response = requests.post(url, json=payload)
    return response.json()

# 使用示例
tx_hash = "GF5tJVe6PZV2DFVhSYRZQSxisoH9YS8fTnGGwBqNcCYJ1jmyBr5VRVcKJRJRsK9TRsyrHmX7K1eEvqgPPvXxSBk"
result = get_solana_transaction(tx_hash)
print(result)
