
# ? Pricing https://www.helius.dev/pricing

import requests
from rich import print
from rich.syntax import Syntax
import json

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


#################################################################################

# # 使用示例
signature = "3sSFXZwWnL9Cbu6nnCapBScFMJFujKoP8TKA37nYk3Ryi3b3yi1QbcCT5xs9mtGmS7CjUgiHESgC8tqbqQvcg4Lk"
# 获取Signer地址
signer = get_signer(signature)
print(f"Signature: {signature}, Signer: {signer}")
