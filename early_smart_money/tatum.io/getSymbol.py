
# ? 文档：https://docs.tatum.io/reference/gettokensv4

import requests

def get_symbol(token_address):
    url = "https://api.tatum.io/v4/data/tokens"
    headers = {
        "accept": "application/json",
        "x-api-key": "t-685a3f207b2cac50cedeba6f-0543689c7fa6497bbcf314bc"
    }
    params = {
        "chain": "solana",
        "tokenAddress": token_address
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        # print(response.json())
        return response.json()["symbol"]
    except requests.exceptions.Timeout:
        print("请求超时")
        return {"error": "timeout"}
    except requests.exceptions.RequestException as e:
        print(f"请求失败：{e}")
        return {"error": str(e)}

##############################################
# 代币合约地址
token_address = "ENfpbQUM5xAnNP8ecyEQGFJ6KwbuPjMwv7ZjR29cDuAb"
symbol = get_symbol(token_address)
print(f"Token Symbol : {symbol}")
