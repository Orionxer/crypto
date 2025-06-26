
# [x] 验证 GetSignaturesForAddress 接口，打印所有键值对，获取哈希签名
# 接口文档 https://solana.com/docs/rpc/http/getsignaturesforaddress

import requests
from rich import print
from rich.syntax import Syntax
import json

def friend_print(response_str):
    json_str = json.dumps(response_str, indent=4, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="dracula", background_color="default")
    print(syntax)

# 根据哈希签名查询在此时间之前的交易哈希签名
# ! 查询数量不能超过1000
def get_signatures_for_address(address, signature):
    url = "https://api.mainnet-beta.solana.com"
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
    response = requests.post(url, json=payload)
    friend_print(response.json())
    return response.json()

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

###########################################################

# 使用示例
# 签名哈希
signature = "GF5tJVe6PZV2DFVhSYRZQSxisoH9YS8fTnGGwBqNcCYJ1jmyBr5VRVcKJRJRsK9TRsyrHmX7K1eEvqgPPvXxSBk"
# 代币合约地址
token_address = "ENfpbQUM5xAnNP8ecyEQGFJ6KwbuPjMwv7ZjR29cDuAb"
# 查询列表
results = get_signatures_for_address_list(token_address, signature)
# 打印列表
for i, (block_time, signature) in enumerate(results, start=1):
    print(f"[{i}] blockTime: {block_time}, signature: {signature}")
