##################################### Solana.py ############################################
# from solana.rpc.api import Client
# from solders.signature import Signature
# solana_client = Client("https://docs-demo.solana-mainnet.quiknode.pro/")
# sig = Signature.from_string("D13jTJYXoQBcRY9AfT5xRtsew7ENgCkNs6mwwwAcUCp4ZZCEM7YwZ7en4tVsoDa7Gu75Jjj2FgLXNUz8Zmgedff")
# print(solana_client.get_transaction(sig, "jsonParsed", max_supported_transaction_version=0))
#############################################################################################

# ? Pricing https://www.quicknode.com/pricing

import requests
from rich import print
from rich.syntax import Syntax
import json

url = "https://docs-demo.solana-mainnet.quiknode.pro/"

payload = {
    "id": 1,
    "jsonrpc": "2.0",
    "method": "getTransaction",
    "params": ["3sSFXZwWnL9Cbu6nnCapBScFMJFujKoP8TKA37nYk3Ryi3b3yi1QbcCT5xs9mtGmS7CjUgiHESgC8tqbqQvcg4Lk"]
}

headers = {
    "accept": "application/json",
    "content-type": "application/json",
}

response = requests.post(url, json=payload, headers=headers)

json_str = json.dumps(response.json(), indent=4, ensure_ascii=False)
syntax = Syntax(json_str, "json", theme="dracula", background_color="default")
print(syntax)
