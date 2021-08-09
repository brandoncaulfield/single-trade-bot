from logging import Logger

import websocket
from helper import *
import os
from websocket import create_connection
import re
from datetime import datetime

####################################################
#                   USER INPUTS                    #
#                                                  #
####################################################
# Is it a test Scenario
test_mode = False

# The time in min between calls to check the price difference
time_difference = 3

# Coin = asset pair to trade (must include currency e.g. XXBTZUSD)
coin = 'XETHZGBP'

# Coin USD rate to not go below
# coin_threshold = 30

# Volatility %
# volatility_percentage = 0.5

# Take Profit (TP) percentage
take_profit = 2

# Stop Los (SL) percentage
stop_loss = 1

# The USD value to spend on each asset
value_to_spend = 2000

# The currency to be used for all trades
trading_currency = 'ZGBP'

# In case of price fluctuations use this safe percentage to ensure order is made
# safe_percentage = 99

# Switch for trailing SL and TP
trailing_sl_and_tp = False


####################################################
#                END OF USER INPUTS                #
#                  Edit with care                  #
####################################################


def run():

    # # Check the price
    # current_price = get_current_price(coin)
    # print(current_price)

    # volume_to_buy = determine_volume_to_buy(current_price, value_to_spend, trading_currency)
    # print(volume_to_buy)
    
    # # Buy the coin
    # order_resp = place_order(coin, "buy", volume_to_buy)

    # if len(order_resp["error"]) == 0:
    #     # Wait for order to propogate
    #     time.sleep(10)

    #     order_info = get_order_info(order_resp["result"]["txid"][0])

    #     trade_data = get_trade_details(order_info['result'][order_resp["result"]["txid"][0]]["trades"][0])

    # else:
    #     raise Exception(order_resp)


    # Connect to WebSocket API and subscribe to trade feed for XBT/USD and XRP/USD
    ws = create_connection("wss://ws.kraken.com/")

    #  ws.send('{"event":"subscribe", "subscription":{"name":"ownTrades", "token": "%s"}}' % token)

    ws.send('{"event":"subscribe", "subscription":{"name":"ohlc"}, "pair":["ETH/USD"]}')


    while True:

        trade_data = ws.recv()

        # print(trade_data)

        data = re.sub(r'[^\w:,/]', '', trade_data)

        data_array = data.split(",")

        # print(data_array)

        if data_array[0] == '551':
            print(f'Close price: {data_array[7]} GBP at {datetime.now()}')



if __name__ == "__main__":
    run()