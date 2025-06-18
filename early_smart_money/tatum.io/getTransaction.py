##############################################################
# ? Pricing https://tatum.io/pricing
import requests
from rich import print
from rich.syntax import Syntax
import json

url = "https://solana-mainnet.gateway.tatum.io/"

payload = {
    "id": 1,
    "jsonrpc": "2.0",
    "method": "getTransaction",
    "params": ["3sSFXZwWnL9Cbu6nnCapBScFMJFujKoP8TKA37nYk3Ryi3b3yi1QbcCT5xs9mtGmS7CjUgiHESgC8tqbqQvcg4Lk"]
}

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "x-api-key": "t-66a730ccccfd17001c479705-2f597d14ad7543f289a03418"
}

response = requests.post(url, json=payload, headers=headers)

json_str = json.dumps(response.json(), indent=4, ensure_ascii=False)
syntax = Syntax(json_str, "json", theme="dracula", background_color="default")
print(syntax)
