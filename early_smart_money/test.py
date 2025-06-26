import requests
import json
from rich import print
from rich.syntax import Syntax

def friend_print(response):
    json_str = json.dumps(response, indent=4, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="dracula", background_color="default")
    print(syntax)

def parse_transaction():

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
    
parse_transaction()
