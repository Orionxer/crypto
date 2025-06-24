
# ? Pricing https://www.helius.dev/pricing

import requests
from rich import print
from rich.syntax import Syntax
import json
import time
from datetime import datetime, timezone

# Helius API密钥
api_key = "99068046-8305-4d16-9c03-b7e6ae63250b"
# 要查询的钱包地址
wallet = "DNfuF1L62WWyW3pNakVkyGGFzVVhj4Yr52jSmdTyeBHm"
# 代币合约地址
token_mint = "ENfpbQUM5xAnNP8ecyEQGFJ6KwbuPjMwv7ZjR29cDuAb"

url = "https://mainnet.helius-rpc.com?"

params = {
    "api-key": api_key
}

headers = {
    "accept": "application/json",
    "content-type": "application/json",
}

# API接口==>>获取交易细节
def get_trasaction(signature):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            signature,
            {
                "commitment": "confirmed",
                "maxSupportedTransactionVersion": 0,
                "encoding": "json"
            }
        ]
    }
    try:
        response = requests.post(url, params=params, json=payload, timeout=10)
        return response.json()
    except requests.exceptions.Timeout:
        print("请求超时")
        return {"error": "timeout"}
    except requests.exceptions.RequestException as e:
        print(f"请求失败：{e}")
        return {"error": str(e)}
    
# API接口==>>查询指定交易哈希之前的交易哈希列表
def get_signatures_for_address(address, signature):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            address,
            {
                "limit": 100,
                "before": signature
            }
        ]
    }
    try:
        response = requests.post(url, params=params, json=payload, timeout=10)
        return response.json()
    except requests.exceptions.Timeout:
        print("请求超时")
        return {"error": "timeout"}
    except requests.exceptions.RequestException as e:
        print(f"请求失败：{e}")
        return {"error": str(e)}
    

def friend_print(response):
    json_str = json.dumps(response, indent=4, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="dracula", background_color="default")
    print(syntax)

def get_signer(signature):
    response = get_trasaction(signature)
    # friend_print(response)
    # TODO 添加容错处理
    if 'result' in response:
        # 获取Signer地址(买入地址)  
        first_account_key = response["result"]["transaction"]["message"]["accountKeys"][0]
    else:
        print("======= Error =======")
        friend_print(response)
        first_account_key = None
    return first_account_key

def get_signatures_for_address_list(address, signature):
    # 查询结果
    response = get_signatures_for_address(address, signature)
    # 打印结果
    # friend_print(response)
    # ** 如果"err"不为null，说明交易异常，则忽略该签名
    results = []
    for transaction in response.get("result", []):
        if transaction.get("err") is None:
            block_time = transaction.get("blockTime")
            signature = transaction.get("signature")
            results.append((block_time, signature))
    return results


#################################################################################

# # # 使用示例
# signature = "3sSFXZwWnL9Cbu6nnCapBScFMJFujKoP8TKA37nYk3Ryi3b3yi1QbcCT5xs9mtGmS7CjUgiHESgC8tqbqQvcg4Lk"
# # 获取Signer地址
# signer = get_signer(signature)
# print(f"Signature: {signature}, Signer: {signer}")

# 签名哈希
signature = "GF5tJVe6PZV2DFVhSYRZQSxisoH9YS8fTnGGwBqNcCYJ1jmyBr5VRVcKJRJRsK9TRsyrHmX7K1eEvqgPPvXxSBk"
# 代币合约地址
token_address = "ENfpbQUM5xAnNP8ecyEQGFJ6KwbuPjMwv7ZjR29cDuAb"
# 查询列表
results = get_signatures_for_address_list(token_address, signature)
print(f"Expect Signatures List Length: {len(results)}")
# 打印列表 
for i, (block_time, signature) in enumerate(results, start=1):
    # 获取Signer地址 
    signer = get_signer(signature)
    # TODO 添加容错处理
    if signer is None:
        print("[Error]: Get Signer Failed, stop...")
        break
    # 转换为可读的UTC时间 # ! 默认0时区，即 +UTC
    human_time = datetime.fromtimestamp(block_time, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{i:03d}] BlockTime: {block_time}, HumanTime: {human_time}, Signature: {signature}, Signer: {signer}")
    if i == len(results):
        print("=======================================")
        print("Every valid data requst success")
