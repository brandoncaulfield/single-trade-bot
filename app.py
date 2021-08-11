import logging
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

# Price to buy at
# price_to_buy = 2000

# Take Profit (TP) percentage
take_profit = 6

# Stop Loss (SL) percentage
stop_loss = 3

# The USD value to spend on each asset
value_to_spend = 2000

# The currency to be used for all trades
trading_currency = 'ZGBP'

# In case of price fluctuations use this safe percentage to ensure order is made
safe_percentage = 99

# Switch for trailing SL and TP
trailing_sl_and_tp = False

# Makes sure to sell if purchase price is hit (Experimental)
hold_the_floor = False

and_now_his_watch_has_ended = False


####################################################
#                END OF USER INPUTS                #
#                  Edit with care                  #
####################################################


def run():

    ''' Logging '''
    logging.basicConfig(filename='app.log', level=logging.INFO)

    print('Hey Ho! Lest Go!')
    logging.info('Hey Ho! Lest Go!')

    # Check the price
    current_price = get_current_price(coin)


    print(f'Current price: {current_price}')
    logging.info(f'Current price: {current_price}')


    if not do_we_own_the_coin(coin):

        # Has the price hit our limit to buy
        # if price_to_buy:

        if test_mode:
            print('test mode')
            logging.info('test mode')

            portfolio_data = {}  
            trade_id = 1234
            portfolio_data[coin] = {}
            portfolio_data[coin]["bought_at"] = float(current_price)
            portfolio_data[coin]["take_profit"] = determine_take_profit(float(current_price), take_profit)
            portfolio_data[coin]["stop_loss"] = determine_stop_loss(float(current_price), stop_loss)
            portfolio_data[coin]["vol"] = float(0.02342424)

            # Add coin to portfolio
            add_coin_to_portfolio(coin, portfolio_data)

            update_order_log(portfolio_data)

            print('Test order complete')
            logging.info('Test order complete')

        else:
            
            volume_to_buy = determine_volume_to_buy(current_price, value_to_spend, trading_currency, safe_percentage)
            print(f'Volume to buy: {volume_to_buy}')
            logging.info(f'Volume to buy: {volume_to_buy}')
            
            try:
                # Buy the coin
                order_resp = place_order(coin, "buy", volume_to_buy)

                if len(order_resp["error"]) == 0:

                    # Wait for order to propogate
                    time.sleep(10)

                    order_info = get_order_info(order_resp["result"]["txid"][0])

                    trade_data = get_trade_details(order_info['result'][order_resp["result"]["txid"][0]]["trades"][0])

                    update_order_log(trade_data)

                    portfolio_data = {}  
                    trade_id = order_info['result'][order_resp["result"]["txid"][0]]["trades"][0]
                    portfolio_data[coin] = {}
                    portfolio_data[coin]["bought_at"] = float(trade_data['result'][trade_id]["price"])
                    portfolio_data[coin]["take_profit"] = determine_take_profit(float(trade_data['result'][trade_id]["price"]), take_profit)
                    portfolio_data[coin]["stop_loss"] = determine_stop_loss(float(trade_data['result'][trade_id]["price"]), stop_loss)
                    portfolio_data[coin]["vol"] = float(trade_data['result'][trade_id]["vol"])


                    # Add coin to portfolio
                    add_coin_to_portfolio(coin, portfolio_data)

                    print(f'We just made a *** REAL *** order: {trade_data}')
                    logging.info(f'We just made a REAL order: {trade_data}')

                    print(f'{coin} added to portfolio')
                    logging.info(f'{coin} added to portfolio')

            except: 
                # print(f'{order_resp}')
                # logging.info(f'{order_resp}')
                print(f'Order failed')
                logging.info(f'Order failed')

           
    else:

        # Always make sure we have the portfolio data we need for the loop below 
        try:
            if not "portfolio_data" in locals():
                portfolio_data = get_portfolio_data(coin)
        except:
            print('There is an issue with the portfolio data')
            logging.info('There is an issue with the portfolio data')

    ''' Connect to Websocket publisher server here'''
    # Then in the While loop send messages as they come based on the Kraken websocket
    '''end'''

    # Connect to WebSocket API and subscribe to trade feed for XBT/USD and XRP/USD
    ws = create_connection("wss://ws.kraken.com/")

    #  ws.send('{"event":"subscribe", "subscription":{"name":"ownTrades", "token": "%s"}}' % token)

    ws.send('{"event":"subscribe", "subscription":{"name":"ohlc"}, "pair":["ETH/GBP"]}')


    #  From here we just keep checking when we need to sell
    while True:

        ohlc = ws.recv()

        data = re.sub(r'[^\w:,/.]', '', ohlc)

        data_array = data.split(",")

        # print(data_array)

        if 'ETH/GBP' in data_array:
            print(f'Close price: {data_array[7]} {trading_currency} at {datetime.now()}')
            logging.info(f'Close price: {data_array[7]} {trading_currency} at {datetime.now()}')
            

            # Check if moved below SMA 50 and 200 line


            # check TP
            if float(data_array[7]) > float(portfolio_data[coin]['take_profit']):
                if test_mode:
                    remove_coin_from_portfolio(coin)

                    order_log_data = {}
                    order_log_data[coin] = {"order_reason":"Take Profit", "price": float(data_array[7])}

                    update_order_log(order_log_data)

                    print(f'TP hit at price: {current_price}')
                    logging.info(f'TP hit at price: {current_price}')

                    if and_now_his_watch_has_ended:
                        break

                else:

                    print(f'TP hit at price: {current_price}')
                    logging.info(f'TP hit at price: {current_price}')

                    order_resp_sl = place_order(coin, 'sell', portfolio_data[coin]['vol'])

                    if len(order_resp_sl["error"]) == 0:
                        # Wait for order to propogate
                        time.sleep(10)

                        order_info = get_order_info(order_resp_sl["result"]["txid"][0])

                        trade_data = get_trade_details(order_info['result'][order_resp_sl["result"]["txid"][0]]["trades"][0])

                        trade_data['portfolio_data'] = portfolio_data

                        trade_data['order_reason'] = 'Take Profit'

                    update_order_log(trade_data)

                    print(f'TP logged successfully')
                    logging.info(f'TP logged successfully')

                    if and_now_his_watch_has_ended:
                        break
            
            # Wha to do if we want a floor price set
            if hold_the_floor:
                
                if float(data_array[7]) <= float(portfolio_data[coin]['bought_at']):

                    if test_mode:
                        remove_coin_from_portfolio(coin)

                        order_log_data = {}
                        order_log_data[coin] = {"order_reason":"Floor price hit", "price": float(data_array[7])}

                        update_order_log(order_log_data)

                        print(f'Floor price hit at price: {portfolio_data[coin]["bought_at"]}')
                        logging.info(f'Floor price hit at price: {portfolio_data[coin]["bought_at"]}')

                        if and_now_his_watch_has_ended:
                            break
                    
                    else:

                        print(f'Floor price hit at price: {portfolio_data[coin]["bought_at"]}')
                        logging.info(f'Floor price hit at price: {portfolio_data[coin]["bought_at"]}')

                        order_resp_floor = place_order(coin, 'sell', portfolio_data[coin]['vol'])

                        if len(order_resp_floor["error"]) == 0:
                            # Wait for order to propogate
                            time.sleep(10)

                            order_info = get_order_info(order_resp_sl["result"]["txid"][0])

                            trade_data = get_trade_details(order_info['result'][order_resp_floor["result"]["txid"][0]]["trades"][0])

                            trade_data['portfolio_data'] = portfolio_data

                            trade_data['order_reason'] = 'Floor Price'

                            update_order_log(trade_data)

                            print(f'Floor price logged successfully')
                            logging.info(f'Floor price logged successfully')

                            if and_now_his_watch_has_ended:
                                break


            # check SL
            if float(data_array[7]) < float(portfolio_data[coin]['stop_loss']):
                if test_mode:
                    remove_coin_from_portfolio(coin)

                    order_log_data = {}
                    order_log_data[coin] = {"order_reason":"Stop Loss", "price": float(data_array[7])}

                    update_order_log(order_log_data)

                    print(f'SL hit at price: {current_price}')
                    logging.info(f'SL hit at price: {current_price}')

                    if and_now_his_watch_has_ended:
                        break
                

                else:

                    print(f'SL hit at price: {current_price}')
                    logging.info(f'SL hit at price: {current_price}')

                    order_resp_sl = place_order(coin, 'sell', portfolio_data[coin]['vol'])

                    if len(order_resp_sl["error"]) == 0:
                        # Wait for order to propogate
                        time.sleep(10)

                        order_info = get_order_info(order_resp_sl["result"]["txid"][0])

                        trade_data = get_trade_details(order_info['result'][order_resp_sl["result"]["txid"][0]]["trades"][0])
                        trade_data['portfolio_data'] = portfolio_data

                        trade_data['order_reason'] = 'Take Profit'

                        update_order_log(trade_data)

                        print(f'SL logged successfully')
                        logging.info(f'SL logged successfully')

                        if and_now_his_watch_has_ended:
                            break
            
            # TODO
            # Keep the loop going
            # Buy
            # Watch
            # Sell
            # Watch
            # Repeat ->

            # IF we hit a stop loss that price becomes the new auto buying price

            # Update trailing Stop Loss
            # Also...
            # Set a "FLOOR" value of what you bought it for for long term strategy
            # If it goes below this floor, wait, and if the price passes the floor
            # then buy again and let it ride. Always be in control so you never lose
            # mmoney from what you bought it at
            # 
            # Allow for a choice of either or options in the paramaters
            # 
            # Also if the price drops below the floor, Sell, then setup the loop to 
            # wait for the price to hit a certian point to buy again (maybe after a
            # rise event. Idea is to bering the floor as low as possible for max profit
            # 

            
             
            print(f'Neither TP: {portfolio_data[coin]["take_profit"]} nor SL: {portfolio_data[coin]["stop_loss"]} nor Floor Price: {portfolio_data[coin]["bought_at"]} was hit')
            logging.info(f'Neither TP: {portfolio_data[coin]["take_profit"]} nor SL: {portfolio_data[coin]["stop_loss"]} nor Floor Price: {portfolio_data[coin]["bought_at"]} was hit')


if __name__ == "__main__":
    run()