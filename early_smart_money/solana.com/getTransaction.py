
# [x] 验证 getTransaction 接口，打印所有键值对，获取买入地址
# 接口文档 https://solana.com/docs/rpc/http/gettransaction

import requests
from rich import print
from rich.syntax import Syntax
import json

# ! 查询太频繁会触发错误 Too many requests for a specific RPC call
def get_trasaction(signature):
    url = "https://api.mainnet-beta.solana.com"
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
        response = requests.post(url, json=payload, timeout=10)
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
    friend_print(response)
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
signature = "HoR9fAXWRUzr8YpUQgbxMBqtS92duY5bdWoGoGJxW3ZJeZSxSwdLpThPfTAdnh6BqQGqJhhSrUR6dnpr9hnyQfT"
# 获取Signer地址
signer = get_signer(signature)
print(f"Signature: {signature}, Signer: {signer}")

