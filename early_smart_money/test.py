import requests
import json
from rich import print
from rich.syntax import Syntax

# 签名哈希
signature = "GF5tJVe6PZV2DFVhSYRZQSxisoH9YS8fTnGGwBqNcCYJ1jmyBr5VRVcKJRJRsK9TRsyrHmX7K1eEvqgPPvXxSBk"
# 代币地址 # ? 暂时无法通过签名哈希查询出代币地址
token_address = "ENfpbQUM5xAnNP8ecyEQGFJ6KwbuPjMwv7ZjR29cDuAb"

def friend_print(response):
    json_str = json.dumps(response, indent=4, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="dracula", background_color="default")
    print(syntax)

def helius_advanced_transaction():

    params = {
        "api-key": "99068046-8305-4d16-9c03-b7e6ae63250b",
    }

    url = "https://api.helius.xyz/v0/transactions/"
    payload = {
        "transactions": ["GF5tJVe6PZV2DFVhSYRZQSxisoH9YS8fTnGGwBqNcCYJ1jmyBr5VRVcKJRJRsK9TRsyrHmX7K1eEvqgPPvXxSBk"]
    }
    response = requests.post(url, params=params, json=payload)

    data = response.json()
    friend_print(data)
    # print("Parsed transaction:", data)
    
# helius_advanced_transaction()

###############################################################
def zan_top(address, signature):
    url = "https://api.zan.top/node/v1/solana/mainnet/80726fc796a4441484c0136524692fbd"

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            address,
            {
                "limit": 10,
                "before": signature
            }
        ]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    friend_print(response.json())

# zan_top(token_address, signature)


def solana_fm_transfer_transactions(hash):
    url = "https://api.solana.fm/v0/transfers/"+hash
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    friend_print(response.json())

# solana_fm_transfer_transactions(signature)

def solana_com_block_transactions(slot):
    url = "https://api.mainnet-beta.solana.com"
    headers = {"Content-Type": "application/json"}

    slot = 339651252  # replace with your desired slot

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBlock",
        "params": [
            slot, 
            {
                "encoding": "json",
                "maxSupportedTransactionVersion": 0,
                "transactionDetails": "accounts",
                "rewards": None
            }
        ]
    }
    result = []
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    # 打印该Slot中所有买入卖出的代币的签名
    # TODO 筛选买入签名，并打印地址
    # TODO 数据库增加 Block 列
    for tx in data["result"]["transactions"]:
        post_token_balances = tx.get("meta", {}).get("postTokenBalances", [])
        pre_token_balances = tx.get("meta", {}).get("preTokenBalances", [])
        all_balances = post_token_balances + pre_token_balances

        if any(balance.get("mint") == token_address for balance in all_balances):
            signatures = tx.get("transaction", {}).get("signatures", [])
            if signatures:
                print(signatures[0])


solana_com_block_transactions(0)
