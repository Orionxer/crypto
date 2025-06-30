import requests
import json
from rich import print
from rich.syntax import Syntax
import math

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

    # slot = 339651252  # replace with your desired slot

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
    # [x] 筛选买入签名，并打印地址
    block_time = data["result"]["blockTime"]
    parent_slot = data["result"]["parentSlot"]
    # TODO 数据库增加 Block 列
    for tx in data["result"]["transactions"]:
        meta = tx.get("meta", {})
        tx_data = tx.get("transaction", {})
        account_keys = tx_data.get("accountKeys", [])
        signature_list = tx_data.get("signatures", [])
        fee = meta.get("fee", 0)

        # 判断交易是否涉及目标代币
        balances = meta.get("postTokenBalances", []) + meta.get("preTokenBalances", [])
        if not any(b.get("mint") == token_address for b in balances):
            continue

        # 获取交易发起地址信息 # 生成器表达式+next函数组合，用于找到第一个满足条件的元素
        signer_info = next((a for a in account_keys if a.get("signer")), None)
        if not signer_info:
            continue
        signer = signer_info["pubkey"]

        # 获取交易发起地址在余额数组中的索引
        try:
            # 列表推导式，将地址合并为列表后进行定位交易发起地址
            signer_index = [a["pubkey"] for a in account_keys].index(signer)
        except ValueError:
            continue

        # 提取签名前后该代币余额
        def get_ui_amount(balances):
            for b in balances:
                if b.get("mint") == token_address and b.get("owner") == signer:
                    amount_info = b.get("uiTokenAmount", {})
                    return amount_info.get("uiAmount", 0.0)
            return 0.0

        post_amount = get_ui_amount(meta.get("postTokenBalances", [])) or 0.0
        pre_amount = get_ui_amount(meta.get("preTokenBalances", [])) or 0.0

        # 判断是否是买入行为（余额增加）
        if post_amount > pre_amount:
            # preBalances[0] 和 postBalances[0] 代表SOL余额，单位 Lamports
            lamports_spent = meta.get("preBalances", [0])[signer_index] - \
                            meta.get("postBalances", [0])[signer_index] - fee
            sol_spent = lamports_spent / 1e9
            print(signature_list[0], signer,
                f"Token: {post_amount - pre_amount}",
                f"SOL: {sol_spent:.6f}")
            # print("fee", fee)
    return block_time
# TODO 只有到达指定时间才能停止查询
slot = 339651252
block_time = solana_com_block_transactions(slot)
print("BlockTime is:", block_time)
