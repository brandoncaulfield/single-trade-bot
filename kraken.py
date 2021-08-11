import os
import time
import json
import requests
import urllib.parse
import hashlib
import hmac
import base64


# Read Kraken API key and secret stored in environment variables
api_url = "https://api.kraken.com"
api_key = os.environ['API_KEY_KRAKEN']
api_sec = os.environ['API_SEC_KRAKEN']


def get_kraken_signature(urlpath, data, secret):

    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()


# Attaches auth headers and returns results of a POST request
def kraken_request(uri_path, data, api_key, api_sec):
    headers = {}
    headers['API-Key'] = api_key
    # get_kraken_signature() as defined in the 'Authentication' section
    headers['API-Sign'] = get_kraken_signature(uri_path, data, api_sec)
    req = requests.post((api_url + uri_path), headers=headers, data=data)
    return req


def add_kraken_order(coin, order_type, volume):
    try:
        # Construct the request and print the result
        resp = kraken_request('/0/private/AddOrder', {
            "nonce": str(int(1000*time.time())),
            "ordertype": "market",
            "type": order_type,
            "volume": volume,
            "pair": coin,
            # "price": 27500
        }, api_key, api_sec)

        return json.loads(resp.text)

    except:
        return "Error while placing buy order"


def get_trade_details(trade_id):
    # Expects trade ID
    try:
        resp = kraken_request('/0/private/QueryTrades', {
            "nonce": str(int(1000*time.time())),
            "txid": trade_id,
            "trades": True
        }, api_key, api_sec)

        return json.loads(resp.text)
    except:
        print("Erro while getting kraken trade details")
        return "Error while getting trade info"


def get_kraken_price(coin):
    url = 'https://api.kraken.com/0/public/Ticker?pair=' + coin
    response = requests.get(url)
    current_prices = response.json()
    # if len(current_prices["error"]) == 0:
    #     return current_prices['result']
    # else:
    return current_prices

def get_order_info(txid):
    try:
        resp = kraken_request('/0/private/QueryOrders', {
            "nonce": str(int(1000*time.time())),
            "txid": txid,
            "trades": True
        }, api_key, api_sec)

        return json.loads(resp.text)
    except:
        print("Erro while getting kraken order details")
        return "Error while getting trade info"


def get_ohlc_data(coin, interval):
    url = 'https://api.kraken.com/0/public/OHLC?pair=' + coin + '&interval=' + str(interval)
    response = requests.get(url)
    ohlc_data = response.json()
    return ohlc_data


def get_account_balance():
    try:
        resp = kraken_request('/0/private/Balance', {
            "nonce": str(int(1000*time.time()))
        }, api_key, api_sec)

        return json.loads(resp.text)
    except:
        print("Erro while getting kraken account balance")
        return "Error while getting account balance"


def run(order_type):
    # resp = get_order_info("O4YDSC-R4ZXR-SGJDBX")
    # if len(resp["error"]) == 0:
    #     print(resp)
    # else:
    #     print(len(resp["error"]))
    #     print(resp["error"])
    resp = add_kraken_order("XETHZGBP", "sell", 0.82615207)
    if resp:
        print(resp)
    # resp = get_account_balance()
    # if resp:
    #     print(resp)


if __name__ == "__main__":
    run("buy")