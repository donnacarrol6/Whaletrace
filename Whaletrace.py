import json
import requests
import time
from datetime import datetime
from typing import Dict

TELEGRAM_TOKEN = ""
TELEGRAM_CHAT_ID = ""

def load_config(path="config.json") -> Dict:
    with open(path) as f:
        return json.load(f)

def send_telegram_message(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, json=payload)

def get_eth_balance(address: str, api_key: str) -> float:
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={api_key}"
    response = requests.get(url).json()
    wei = int(response["result"])
    return wei / 1e18

def monitor_wallets():
    config = load_config()
    api_key = config["etherscan_api_key"]
    addresses = config["wallets"]
    threshold = config.get("alert_threshold", 100)  # ETH
    state_file = "wallet_state.json"

    try:
        with open(state_file) as f:
            old_state = json.load(f)
    except FileNotFoundError:
        old_state = {}

    new_state = {}

    for addr in addresses:
        balance = get_eth_balance(addr, api_key)
        new_state[addr] = balance
        prev_balance = old_state.get(addr, 0)
        delta = balance - prev_balance

        if abs(delta) >= threshold:
            send_telegram_message(
                f"[Whaletrace] 🐋 Movement detected!\nAddress: {addr}\nChange: {delta:.2f} ETH\nNew Balance: {balance:.2f} ETH\nTime: {datetime.utcnow().isoformat()} UTC"
            )

    with open(state_file, "w") as f:
        json.dump(new_state, f)

if __name__ == "__main__":
    config = load_config()
    TELEGRAM_TOKEN = config.get("telegram_token", "")
    TELEGRAM_CHAT_ID = config.get("telegram_chat_id", "")
    monitor_wallets()

